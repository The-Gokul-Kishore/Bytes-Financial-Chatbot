# import os
import argparse
import traceback
import json
from sqlalchemy.orm import Session
from langchain.agents import AgentType, Tool, initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain_experimental.tools import PythonREPLTool
# from typing import Optional, List, Any
import os
from bytes.database.db import DBManager
from bytes.retriver.PostgresChatMemoryStore import PostgresChatMemoryStore
from bytes.retriver.retriver import  Retriver
#from bytes.agent_services.bedrock_llm_wrapper import BedrockLLM
from bytes.agent_services.agent_schemas import ExtractedInsights
parser = PydanticOutputParser(pydantic_object=ExtractedInsights)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    max_output_tokens=4000,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)



retriver = Retriver()
class Agent_Service:
    def __init__(self,model:str,db_manager:DBManager) -> None:
        self.model = model
        self.db_manager = DBManager()
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0.3,
            max_output_tokens=4000,
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )
        self.db_manager = db_manager
    def get_context(self,query: str) -> tuple[str, list[dict]]:
        results = retriver.retrive(query)
        source_json = []
        prompt = ""
        for doc in results:
            metadata = doc.metadata
            page = metadata.get("page_number", "unknown")
            content = doc.page_content
            prompt += f"[Page {page}]\n{content}\n\n"
            source_json.append({"page": page, "content": content})
        return prompt.strip(), source_json

    def get_prompt(self,query: str, context: str) -> str:
        return f"""
        the user request is as follows : {query}

        answer based on the relevant documents based on the query:
        You are an AI assistant helping summarize financial documents.

        Given the following page excerpts, return a JSON response with:
        1. explanation: A summary or answer to the question
        2. sources: A list of sources used, each with:
        - page: the page number
        - content: the raw text or table used (trimmed if needed)

        #PLS return in this JSON Format
        {{ 
        "explanation": "...",
        "sources": [
            {{
            "type": "text",
            "page": 2,
            "content": "..."
            }}
        ]
        }}
        If no relevant information is found, respond with:
        {{
        "explanation": "No relevant data found in the provided documents.",
        "sources": []
        }}

        ### Provided document excerpts:

        {context}

        ### Respond ONLY with the JSON object as described.
        """


    def explain_with_sources(self,query: str,) -> str:
        context, source_json = self.get_context(query)
        prompt = self.get_prompt(query, context)

        try:
            llm_result = llm.invoke(prompt)

            # Normalize output to dict
            if isinstance(llm_result, dict):
                raw_output = llm_result
            elif hasattr(llm_result, "content"):
                raw_output = json.loads(llm_result.content.strip("json\n").strip())
            elif isinstance(llm_result, str):
                raw_output = json.loads(llm_result.strip("json\n").strip())
            else:
                raise ValueError("Unknown response format from LLM")

            # Pydantic parser expects string input
            parsed_result = parser.parse(json.dumps(raw_output))

        except Exception as e:
            print("❌ Error parsing JSON:", e)
            return {"result": str(llm_result), "source": source_json}

        return {"result": parsed_result.model_dump(), "source": source_json}

    def build_extract_pdf_insights(self):    
            extract_pdf_insights = Tool(
                name="extract_pdf_insights",
                func=self.explain_with_sources,
                description=(
                    "Use this tool to answer ANY question about a company's PDF document. "
                    "If the question includes financial terms like 'revenue', 'profit', 'growth', 'FY2023', etc., "
                    "you MUST use this tool to extract the answer from PDF sources."
                ),
            )
            return extract_pdf_insights
    def build_repl_tool(self):
        repl_tool = PythonREPLTool()
        return repl_tool
    

    def extract_page_excerpt(self,page: int) -> str:
        results = retriver.vectorstore.similarity_search_by_metadata(metadata={"page_number": page}, k=3)
        if not results:
            return f"No content found on page {page}"
        excerpts = [f"[Page {page}]\n{doc.page_content}" for doc in results]
        return "\n\n".join(excerpts)
    def build_page_excerpt_tool(self):
        page_excerpt_tool = Tool(
            name="get_page_excerpt",
            func=self.extract_page_excerpt,
            description="Use this to retrieve the full content of a specific page in the document."
        )
        return page_excerpt_tool

    def run_agent(self,query: str, thread_id: int,db:Session)->dict:
        """
        Run the main agent of the financial insight agent
        Args:
            query (str): The query to run the agent on
            thread_id (int): The thread id of the thread(chat)
        returns:
            dict: The response from the agent
            {
                "text_explanation": "...",
                "chart_json": "...",
                "table_json": "..."
            }
        """
        tools_for_main_agent = [self.build_extract_pdf_insights(), self.build_page_excerpt_tool(), self.build_repl_tool()]
        main_agent_prompt = """
            You are a master financial analyst. Your job is to provide a comprehensive answer to the user's query by orchestrating specialized tools.

            WORKFLOW:
            1.  First, you MUST use the extract_pdf_insights tool to get the related data from the document.
            2.  Review the explanation from the output of the first tool.
            3.  For charts:
                i.  Write Python code using plotly to create a chart.
                ii.  Assign the chart to variable `fig`, convert to JSON using `fig.to_json()` and print it.
            4.  Finally, synthesize the explanation and chart into a full answer.
            pls finish this within 3 calls if more calls are needed return "I cannot answer this question, please try another one"
            Final output format:
            <text_explanation></text_explanation>
            <chart_json>...</chart_json>
            <table_json>...</table_json>
            Start!
            """
        main_agent = initialize_agent(
                tools=tools_for_main_agent,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                memory=PostgresChatMemoryStore(db_manager=db, thread_id=thread_id),
                agent_kwargs={"prefix": main_agent_prompt}
            )

        try:
                response = main_agent.invoke({"input": query})
                print("\n" + "="*50)
                print("✅ FINAL AGENT RESPONSE:")
                print("="*50)
                print(response.get('output'))
                output = (response.get('output'))
                text_explanation = output.split("<text_explanation>")[1].split("</text_explanation>")[0]
                chart_json = output.split("<chart_json>")[1].split("</chart_json>")[0]
                table_json = output.split("<table_json>")[1].split("</table_json>")[0]
                return {
                    "text_explanation": text_explanation,
                    "chart_json": chart_json if len(chart_json) > 0 else None,
                    "table_json": table_json if len(table_json) > 0 else None
                }
        except Exception as e:
                print("error:", e)
                print(f"\nAn error occurred in the main agent execution: {traceback.format_exc()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run financial insight agent.")
    parser.add_argument("--prompt", type=str, required=True, help="User query to run the agent on")
    args = parser.parse_args()

    Agent_Service.run_agent(args.prompt)

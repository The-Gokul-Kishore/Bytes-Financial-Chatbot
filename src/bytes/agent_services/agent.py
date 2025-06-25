from __future__ import annotations

import traceback
import json

from sqlalchemy.orm import Session
from langchain.agents import AgentType,  initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain_experimental.tools import PythonREPLTool
# from typing import Optional, List, Any
import os
from typing import Optional
# from langchain_core.runnables import RunnableWithMessageHistory
from bytes.database.db import DBManager
# from bytes.retriver.PostgresMessageHistory import PostgresMessageHistory
from bytes.retriver.retriver import  Retriver
#from bytes.agent_services.bedrock_llm_wrapper import BedrockLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from bytes.agent_services.agent_schemas import ExtractedInsights, FinancialOutput
from pydantic_ai import Agent,Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dataclasses import dataclass
from pydantic_graph import BaseNode,End,Graph,GraphRunContext


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
    def get_context(self, query: str, thread_id: int = 0) -> tuple[str, list[dict]]:
        results = retriver.retrive(query, thread_id=thread_id)
        source_json = []
        prompt = ""

        for doc in results:
            metadata = doc.metadata
            doc_id = metadata.get("doc_id", "unknown_id")
            content = doc.page_content
            prompt += f"[doc_id: {doc_id}]\n{content}\n\n"
            source_json.append({"doc_id": doc_id, "content": content})

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


    def explain_with_sources(self,query: str,thread_id:int=0) -> str:
        context, source_json = self.get_context(query,thread_id)
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

    def build_extract_pdf_insights(self,thread_id:int=0):    
            extract_pdf_insights = Tool(
                name="extract_pdf_insights",
                func=lambda query: self.explain_with_sources(query=query,thread_id=thread_id),
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
    

    def extract_excerpt_per_doc_id(self,doc_id:str,thread_id:int=0) -> str:
        results = retriver.vectorstore.similarity_search_by_metadata(metadata={"doc_id": doc_id,"thread_id":thread_id}, k=3)
        if not results:
            return f"No content found on page {doc_id}"
        excerpts = [f"[doc_id{doc.metadata['doc_id']}]\n{doc.page_content}" for doc in results]
        return "\n\n".join(excerpts)
    def build_page_excerpt_tool(self,thread_id:int=0):
        get_doc_id_excerpt = Tool(
            name="get_doc_id_excerpt",
            func=lambda doc_id: self.extract_excerpt_per_doc_id(doc_id=doc_id,thread_id=thread_id),
            description="Use this to retrieve the full content of a specific document excerpt specifed by doc_id in the document."
        )
        return get_doc_id_excerpt
    def fix_output(self,output:str)->dict:
        try:
            parser = PydanticOutputParser(pydantic_object=FinancialOutput)
            fix_prompt_template = PromptTemplate(
                    template="""
                    You're a strict JSON formatter.

                    Here is a messy or partially structured response:
                    ----------------
                    {response}
                    ----------------

    Your job is to convert it to valid JSON matching this schema:
    {{"text_explanation": str, "chart_json": Optional[str], "table_json": Optional[dict]}}

                    Return only a valid JSON object. No text, no commentary, no extra formatting.
                    """,
                    input_variables=["response"]

            )
            refine_chain = LLMChain(
                llm = llm,
                prompt=fix_prompt_template,
                output_parser=parser
            )
            structured_output = refine_chain.run({"response": output})
            return structured_output
        except Exception as e:
            print("error:", e)
            return f"error: {e}"
    def run_agent(self,query: str, thread_id: int,db:Session,thread_specific_call:bool=False)->dict:
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
        if(thread_specific_call):
            passing_id = thread_id
        else:
            passing_id = 0
        tools_for_main_agent = [self.build_extract_pdf_insights(thread_id=passing_id), self.build_page_excerpt_tool(thread_id=passing_id), self.build_repl_tool()]
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
            {
            "text_explanation": "your explanation here",
            "chart_json": "...plotly fig.to_json() string here...",
            "table_json": {...}  // if not applicable, return null
            }

            ⚠️ DO NOT include markdown, HTML, or extra commentary — return only the JSON object.
            ⚠️ If the answer can't be completed in 3 steps, respond with:
            { "text_explanation": "I cannot answer this question, please try another one", "chart_json": null, "table_json": null }

            Start!
            """
        main_agent = initialize_agent(
                tools=tools_for_main_agent,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                agent_kwargs={"prefix": main_agent_prompt}
            )
        # runnable = RunnableWithMessageHistory(
        #      main_agent,
        #      lambda session_id: PostgresMessageHistory(db_manager=db, thread_id=session_id),
        #      input_messages_key="input",
        #      history_messages_key="chat_history",
        # )
        try:
                print("\n" + "="*50)
                print("🤖 AGENT PROMPT:")
                response = main_agent.invoke({"input": query},
                                           config={"configurable":{"session_id":str(passing_id)}}
                                           )
                print("\n" + "="*50)
                print("✅ FINAL AGENT RESPONSE:")
                print("="*50)
                if(response.get("output") is None):
                    return {"text_explanation": "I cannot answer this question, please try another one", "chart_json": None, "table_json": None}
                print(response.get('output'))
                output_raw = response.get('output')
                try:
                    output_raw = str(output_raw)
                    output = self.fix_output(output=output_raw)
                    output = json.loads(output) if isinstance(output, str) else output
                    return output
                except json.JSONDecodeError:
                    print("⚠️ Model did not return valid JSON!")
                    return {
                        "text_explanation": "Model returned invalid JSON. Try another query.",
                        "chart_json": None,
                        "table_json": None
                    }
                # return {
                #     "text_explanation": output.get("text_explanation"),
                #     "chart_json": chart_json if len(chart_json) > 0 else None,
                #     "table_json": table_json if len(table_json) > 0 else None
                # }     
        except Exception as e:
                print("error:", e)
                print(f"\nAn error occurred in the main agent execution: {traceback.format_exc()}")
        """_summary_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
@dataclass
class State:
    user_query:str
    context:str
    text:str
    chart_json:Optional[str]
    table_json:Optional[dict]
    thread_id:int

def execute_code(exec_code:str)->str:
    """exectues python code and returns value of the variable named fig_json
"import plotly.graph_objects as go\nfig = go.Figure(data=[go.Bar(x=['Growth', 'Revenue', 'Category1', 'Category2', 'Category3'], y=[2.2, 13.4, 926, 1385, 29.1])])\nfig.update_layout(title='FY 2024 Data', xaxis_title='Categories', yaxis_title='Values')\nfig_json = fig.to_json()\nprint(fig_json)"
    Args:
        exec_code (str): python code creating fig and subsequently fig_json

    Returns:
        str: fig_json
    """
    try:
        locals = {}
        exec(exec_code,{"px":px,"go":go,"pd":pd,"pio":pio},locals)
        if("fig_json" in locals):
            return locals.get("fig_json")
        else:
            raise Exception("fig_json not found")
    except Exception as e:
        print("error:", e)
        return f"error: {e}"
class summarizerResponse(BaseModel):
    text:str
    table_json:Optional[dict]
    is_graph_needed:bool
    graph_instructions:str
class graphResponse(BaseModel):
    graph_json:str
@dataclass
class RetriverAgent(BaseNode[State]):
    def get_context(self, query: str, thread_id: int = 0,k:int=10) -> tuple[str, list[dict]]:
        results = retriver.retrive(query, thread_id=thread_id,k=k)
        source_json = []
        prompt = ""

        for doc in results:
            metadata = doc.metadata
            doc_id = metadata.get("doc_id", "unknown_id")
            content = doc.page_content
            page = metadata.get("page_number", "unknown_page")
            prompt += f"[doc_id: {doc_id}] page: {page}\n\n{content}\n\n"  
            source_json.append({"doc_id": doc_id, "content": content})

        return prompt.strip(), source_json

    async def run(self,ctx:GraphRunContext[State])->SummarizerAgent:
        ctx.state.context, sources = self.get_context(ctx.state.user_query, thread_id=ctx.state.thread_id,k=5)
        return SummarizerAgent()
@dataclass
class SummarizerAgent(BaseNode[State]):
    def get_prompt(self,query: str, context: str) -> str:
        return f"""
        you are a summarize assitant , 
        with a bunch of document chunks based on which you need to answer the below query
        the user request is as follows : {query}
        answer based on the relevant documents based on the query:
        {context}
        make sure to include a consice answer to the query and also if needed the table from the docuemnt excrpts
        and also if graph is needed provide the graph instructions for it and set the is_graph_needed to true
        
        You must respond by calling the `final_result` function. Do NOT output freeform text.

            Always call the `final_result` function with this input:

           
            "text": "...your summary here...",
            "table_json": {...} or null,
            "is_graph_needed": True or False,
            "graph_instructions": "...if any..."
            
    

        """
    async def run(self,ctx:GraphRunContext[State])->GraphAgent|End:
        prompt = self.get_prompt(ctx.state.user_query, ctx.state.context)
        response = await ctx.deps.summarizer_agent.run(prompt)
        ctx.state.text = response.output.text
        ctx.state.table_json = response.output.table_json
        is_graph_needed = response.output.is_graph_needed
        return GraphAgent(instructions=response.output.graph_instructions) if is_graph_needed else End(ctx)
    
@dataclass    
class GraphAgent(BaseNode[State]):
    instructions:str
    def get_prompt(self) -> str:
        prompt = f"""
        You are a viualizer agent, you are given a instructions to write a python plotly code to create a graph
        from the provided instructions using the plotly libary and using the repl tool using the tool call
        and ensure to return the plotly fig.to_json()
        and print it in the code genrated
        instructions: {self.instructions}

        use the execute_code tool to execute the python code and return the fig_json
        You are a graph agent. You are given instructions to generate a Python code block using Plotly.

You MUST call the tool `execute_code` by returning a function call with this structure:

{{
  "exec_code": "your python code as a string"
}}

Use `fig = go.Figure(...)` and at the end, assign `fig_json = fig.to_json()` .

Do NOT return code inline. Do NOT use angle brackets. Do NOT write prose. Only return a function call to `execute_code` with one string argument.
You must call the function `final_result` by returning only structured JSON.

Return ONLY a tool call like this:

{{
  "name": "final_result",
  "parameters": {{
    "graph_json": "..."
  }}
}}

Do NOT use angle brackets, markdown, or pseudo-XML.

    """
        return prompt
    async def run(self,ctx:GraphRunContext[State])->End:
        prompt = self.get_prompt()
        response = await ctx.deps.graph_agent.run(prompt)
        ctx.state.chart_json = response.output.graph_json
        return End(ctx.state)
    
@dataclass        
class Deps():
    summarizer_agent:Agent
    graph_agent:Agent

class AgentRunner:
    def __init__(self, model_name: str, api_key: str):
        self.model = OpenAIModel(
            model_name=model_name,
            provider=OpenAIProvider(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key,
            ),
        )
        self.summarize_agent = self._create_summarizer_agent()
        self.graph_agent = self._create_graph_agent()

    def _create_summarizer_agent(self) -> Agent[summarizerResponse]:
        return Agent(
            model=self.model,
            system_prompt=(
                "You are a summarizer agent. Provide a summary of the text, "
                "include tables if relevant, and instructions for a graph if needed."
            ),
            output_type=summarizerResponse,
            output_retries=3,
        )

    def _create_graph_agent(self) -> Agent[graphResponse]:
        return Agent(
            model=self.model,
            system_prompt=(
                "You are a graph agent. Write Python Plotly code using tool calling "
                "to generate a figure and return fig.to_json()."
            ),
            output_type=graphResponse,
            tools=[Tool(execute_code, takes_ctx=False)],
            output_retries=3,
        )

    async def run(self, user_query: str, thread_id: int = 0) -> dict:
        state = State(
            user_query=user_query,
            context="",
            text="",
            chart_json=None,
            table_json=None,
            thread_id=thread_id
        )

        deps = Deps(
            summarizer_agent=self.summarize_agent,
            graph_agent=self.graph_agent
        )

        graph = Graph(nodes=(RetriverAgent(), SummarizerAgent, GraphAgent))
        result = await graph.run(RetriverAgent(), state=state, deps=deps)

        return {
            "text": result.state.text,
            "table_json": result.state.table_json,
            "graph_json": result.state.chart_json
        }
async def run_agent(user_query: str, thread_id: int = 0):
    model = OpenAIModel(
        
        model_name=os.getenv("MODEL_TYPE", "none"),
        provider=OpenAIProvider(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        ),
    )

    summarize_agent:Agent[summarizerResponse]= Agent(
        model=model,
        system_prompt="You are a summarizer agent give insightful summary of the provided text and also if needed provide the table from the docuemnt excrpts and instructions to create a graph if needed",
        output_type= summarizerResponse,
        output_retries=3,
    )
    graph_agent:Agent[graphResponse]= Agent(
        model=model,
        system_prompt="You are a graph agent write a python plotly code to create a graph from the provided instructions using the plotly libary and use tool calling",
        output_type= graphResponse,
        tools= [Tool(execute_code,takes_ctx=False)],
        output_retries=3,
    )
    state = State(user_query=user_query, context="", text="", chart_json=None, table_json=None, thread_id=thread_id)
    graph = Graph(nodes=(RetriverAgent(),SummarizerAgent,GraphAgent))
    deps = Deps(summarizer_agent=summarize_agent,graph_agent=graph_agent)
    result = await graph.run(RetriverAgent(),
                            state= state,
                             deps=deps)
    
    print("result is:")
    print(result)
    print(result.state.text)
    answer_dict = {
        "text": result.state.text,
        "table_json": result.state.table_json,
        "graph_json": result.state.chart_json if result.state.chart_json else None
    }
    return answer_dict
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv(r"D:\projects\dtcc-i-h-2025-just-a-byte\.env")
    asyncio.run(run_agent("give me a summary of the document and some graph"))
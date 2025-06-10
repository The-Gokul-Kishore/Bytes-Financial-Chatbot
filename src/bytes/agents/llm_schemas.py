from pydantic import BaseModel, Field


class Source(BaseModel):
    type: str = Field(..., description="Whether the source is a 'text' or 'table'")
    page: int = Field(..., description="Page number of the source")
    content: str = Field(..., description="The raw text or table used")


class ExtractedInsights(BaseModel):
    explanation:str = Field(..., description="A summary or direct answer")
    sources: list[Source] = Field(..., description="A list of sources used, each with page number and content")


class GraphResult(BaseModel):
    code:str = Field(..., description="A Python code block")
    html:str = Field(..., description="A HTML code block")
    inisghts:ExtractedInsights = Field(..., description="A summary or direct answer")


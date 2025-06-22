from pydantic import BaseModel, Field
from typing import Optional
class Source(BaseModel):
    type: str = Field(..., description="Whether the source is a 'text' or 'table'")
    page: int = Field(..., description="Page number of the source")
    content: str = Field(..., description="The raw text or table used")


class ExtractedInsights(BaseModel):
    explanation: str = Field(..., description="A summary or direct answer")
    sources: list[Source] = Field(..., description="A list of sources used, each with page number and content")

class FinancialOutput(BaseModel):
    text_explanation: str
    chart_json: Optional[str]
    table_json: Optional[dict]

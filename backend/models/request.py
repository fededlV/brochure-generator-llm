from typing import Literal
from pydantic import BaseModel, Field


class BrochureRequest(BaseModel):
    url: str = Field(
        ...,
        description="Target company website URL to research (e.g. 'https://huggingface.co')",
        examples=["https://huggingface.co"]
    )
    audience: Literal["general", "prospects", "investors", "candidates"] = Field(
        default="general",
        description="Target audience for the marketing brochure"
    )
    tone: Literal["professional", "energetic", "minimalist"] = Field(
        default="professional",
        description="Editorial tone and voice of the brochure"
    )
    max_subpages: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum number of secondary pages to crawl and synthesize"
    )

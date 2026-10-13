import json
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    gemini_configured: bool
    model: str


class SelectedLink(BaseModel):
    url: str
    reason: str


class StatusEventData(BaseModel):
    step: Literal[
        "validating",
        "crawling_landing",
        "analyzing_links",
        "crawling_subpages",
        "generating_brochure",
        "done"
    ]
    message: str
    progress: int = Field(..., ge=0, le=100)


class LinksSelectedEventData(BaseModel):
    selected_links: List[SelectedLink]


class TokenEventData(BaseModel):
    chunk: str


class CompleteEventData(BaseModel):
    status: str = "completed"
    total_pages_crawled: int
    elapsed_seconds: float
    company_name: Optional[str] = None


class ErrorEventData(BaseModel):
    error: str


def format_sse_event(event_name: str, data: Any) -> str:
    """
    Format payload into standard Server-Sent Event (SSE) wire format.
    """
    if isinstance(data, BaseModel):
        payload = data.model_dump_json()
    elif isinstance(data, (dict, list)):
        payload = json.dumps(data)
    else:
        payload = str(data)

    return f"event: {event_name}\ndata: {payload}\n\n"

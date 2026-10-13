import logging
import time
from typing import AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.config import settings
from backend.models.request import BrochureRequest
from backend.models.response import (
    HealthResponse,
    StatusEventData,
    LinksSelectedEventData,
    SelectedLink,
    TokenEventData,
    CompleteEventData,
    ErrorEventData,
    format_sse_event,
)
from backend.services.crawler import validate_url, crawl_page, crawl_multiple_pages
from backend.services.ai_engine import ai_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generation"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check backend status, version, and Gemini API readiness.
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        gemini_configured=settings.is_api_key_valid(),
        model=settings.gemini_model,
    )


async def sse_brochure_pipeline(request: BrochureRequest) -> AsyncGenerator[str, None]:
    """
    Pipeline orchestrating crawling, AI link filtering, subpage fetching,
    and token-by-token brochure synthesis, yielded as Server-Sent Events.
    """
    start_time = time.time()

    # Step 1: Validate URL & SSRF checks
    yield format_sse_event(
        "status",
        StatusEventData(
            step="validating",
            message="Validating target URL...",
            progress=5
        )
    )

    try:
        target_url = validate_url(request.url)
    except ValueError as e:
        yield format_sse_event("error", ErrorEventData(error=f"Invalid URL: {str(e)}"))
        return

    # Check API key readiness
    if not settings.is_api_key_valid():
        yield format_sse_event(
            "error",
            ErrorEventData(
                error="Gemini API key is not configured on the server. Please set GEMINI_API_KEY in .env"
            )
        )
        return

    try:
        # Step 2: Crawl Landing Page
        yield format_sse_event(
            "status",
            StatusEventData(
                step="crawling_landing",
                message=f"Crawling landing page for {target_url}...",
                progress=15
            )
        )

        landing = await crawl_page(target_url)
        if not landing.success:
            yield format_sse_event(
                "error",
                ErrorEventData(error=f"Could not reach website: {landing.error or 'Unknown error'}")
            )
            return

        if not landing.text:
            yield format_sse_event(
                "error",
                ErrorEventData(error="Landing page returned no readable text content.")
            )
            return

        # Step 3: Analyze candidate links using Gemini
        yield format_sse_event(
            "status",
            StatusEventData(
                step="analyzing_links",
                message=f"Analyzing {len(landing.links)} candidate links with Gemini...",
                progress=35
            )
        )

        selected_links_raw = await ai_engine.select_relevant_links(
            landing_url=landing.url,
            landing_text=landing.text,
            candidate_links=landing.links,
            max_selection=request.max_subpages
        )

        selected_models = [
            SelectedLink(url=item["url"], reason=item["reason"])
            for item in selected_links_raw
        ]
        yield format_sse_event("links_selected", LinksSelectedEventData(selected_links=selected_models))

        # Step 4: Concurrently crawl selected subpages
        subpages_content = []
        if selected_models:
            yield format_sse_event(
                "status",
                StatusEventData(
                    step="crawling_subpages",
                    message=f"Fetching {len(selected_models)} selected subpages...",
                    progress=60
                )
            )

            urls_to_fetch = [link.url for link in selected_models]
            subpage_results = await crawl_multiple_pages(urls_to_fetch, max_concurrent=3)
            for page in subpage_results:
                if page.success and page.text:
                    subpages_content.append({
                        "url": page.url,
                        "title": page.title,
                        "text": page.text
                    })

        # Step 5: Synthesize and stream the brochure
        yield format_sse_event(
            "status",
            StatusEventData(
                step="generating_brochure",
                message=f"Synthesizing brochure tailored for {request.audience} in {request.tone} tone...",
                progress=80
            )
        )

        async for chunk in ai_engine.generate_brochure_stream(
            company_url=landing.url,
            landing_content=landing.text,
            subpages_content=subpages_content,
            audience=request.audience,
            tone=request.tone
        ):
            yield format_sse_event("token", TokenEventData(chunk=chunk))

        # Step 6: Completion
        elapsed = round(time.time() - start_time, 2)
        yield format_sse_event(
            "complete",
            CompleteEventData(
                status="completed",
                total_pages_crawled=1 + len(subpages_content),
                elapsed_seconds=elapsed,
                company_name=landing.title or target_url
            )
        )

    except Exception as exc:
        logger.exception("Pipeline execution failed: %s", exc)
        yield format_sse_event("error", ErrorEventData(error=f"Brochure generation failed: {str(exc)}"))


@router.post("/generate/stream")
async def generate_brochure_stream_endpoint(request: BrochureRequest):
    """
    Stream live progress and generated brochure markdown tokens using Server-Sent Events (SSE).
    """
    return StreamingResponse(
        sse_brochure_pipeline(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

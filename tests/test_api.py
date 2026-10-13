import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.services.crawler import PageCrawlResult
from backend.services.ai_engine import ai_engine
from backend.config import settings, Settings


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "gemini_configured" in data
        assert "model" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "AI Company Brochure Generator API is running" in data["message"]


@pytest.mark.asyncio
async def test_generate_stream_invalid_url():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/generate/stream",
            json={"url": "http://127.0.0.1:8000"}  # SSRF blocked URL
        )
        assert response.status_code == 200
        lines = response.text.splitlines()
        # Should contain error event
        assert any("event: error" in line for line in lines)
        assert any("Private or local network" in line for line in lines)


@pytest.mark.asyncio
async def test_generate_stream_missing_api_key():
    transport = ASGITransport(app=app)
    # Temporarily set API key invalid
    with patch.object(Settings, "is_api_key_valid", return_value=False):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/generate/stream",
                json={"url": "https://example.com"}
            )
            assert response.status_code == 200
            assert "Gemini API key is not configured" in response.text


@pytest.mark.asyncio
async def test_generate_stream_full_success_pipeline():
    transport = ASGITransport(app=app)

    landing_result = PageCrawlResult(
        url="https://mockstartup.io",
        title="MockStartup AI",
        text="MockStartup provides AI-powered developer workflows.",
        links=["https://mockstartup.io/about", "https://mockstartup.io/pricing"],
        success=True
    )

    subpage_result = PageCrawlResult(
        url="https://mockstartup.io/about",
        title="About MockStartup",
        text="Founded in 2024 to make software development effortless.",
        links=[],
        success=True
    )

    mock_links_selection = [
        {"url": "https://mockstartup.io/about", "reason": "Describes founding and mission"}
    ]

    async def mock_stream_tokens(*args, **kwargs):
        yield "# MockStartup Brochure\n\n"
        yield "Building the future of developer tools."

    with patch.object(Settings, "is_api_key_valid", return_value=True), \
         patch("backend.routers.generate.crawl_page", AsyncMock(return_value=landing_result)), \
         patch("backend.routers.generate.crawl_multiple_pages", AsyncMock(return_value=[subpage_result])), \
         patch.object(ai_engine, "select_relevant_links", AsyncMock(return_value=mock_links_selection)), \
         patch.object(ai_engine, "generate_brochure_stream", mock_stream_tokens):

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/generate/stream",
                json={
                    "url": "https://mockstartup.io",
                    "audience": "investors",
                    "tone": "professional",
                    "max_subpages": 2
                }
            )

            assert response.status_code == 200
            body = response.text

            # Assert event types are streamed
            assert "event: status" in body
            assert "event: links_selected" in body
            assert "event: token" in body
            assert "event: complete" in body

            # Assert brochure tokens are present
            assert "# MockStartup Brochure" in body
            assert "Building the future of developer tools" in body

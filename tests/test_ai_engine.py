import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from backend.config import Settings
from backend.services.prompts import (
    build_link_selection_user_prompt,
    build_brochure_system_prompt,
    build_brochure_user_prompt,
    AUDIENCE_DIRECTIVES,
    TONE_DIRECTIVES,
)
from backend.services.ai_engine import AIEngine


def test_settings_api_key_resolution():
    s1 = Settings(_env_file=None, gemini_api_key="AIzaSyTest123456789")
    assert s1.effective_api_key == "AIzaSyTest123456789"
    assert s1.is_api_key_valid() is True

    s3 = Settings(_env_file=None, api_key_generic="GenericAPIKey12345")
    assert s3.effective_api_key == "GenericAPIKey12345"
    assert s3.is_api_key_valid() is True

    s4 = Settings(_env_file=None)
    assert s4.is_api_key_valid() is False


def test_build_link_selection_user_prompt():
    prompt = build_link_selection_user_prompt(
        landing_url="https://example.com",
        landing_text="Sample Landing Content",
        candidate_links=["https://example.com/about", "https://example.com/pricing"],
        max_selection=3,
    )
    assert "https://example.com" in prompt
    assert "Sample Landing Content" in prompt
    assert "- https://example.com/about" in prompt
    assert "- https://example.com/pricing" in prompt
    assert "Select at most 3" in prompt


def test_build_brochure_system_prompt():
    investor_prompt = build_brochure_system_prompt(audience="investors", tone="minimalist")
    assert "investor" in investor_prompt.lower()
    assert AUDIENCE_DIRECTIVES["investors"] in investor_prompt
    assert TONE_DIRECTIVES["minimalist"] in investor_prompt


def test_build_brochure_user_prompt():
    subpages = [
        {"url": "https://example.com/about", "title": "About Page", "text": "About us text details."},
        {"url": "https://example.com/careers", "title": "Careers Page", "text": "Join our team."},
    ]
    prompt = build_brochure_user_prompt(
        company_url="https://example.com",
        landing_content="Landing Page Content",
        subpages_content=subpages,
    )
    assert "=== LANDING PAGE CONTENT ===" in prompt
    assert "About Page (https://example.com/about)" in prompt
    assert "Careers Page (https://example.com/careers)" in prompt


def test_parse_link_selection_json_standard():
    engine = AIEngine(api_key="mock_key")
    json_text = json.dumps({
        "selected_links": [
            {"url": "https://example.com/about", "reason": "About us page"},
            {"url": "https://example.com/pricing", "reason": "Pricing details"}
        ]
    })
    parsed = engine._parse_link_selection_json(json_text, [])
    assert len(parsed) == 2
    assert parsed[0]["url"] == "https://example.com/about"
    assert parsed[1]["reason"] == "Pricing details"


def test_parse_link_selection_json_with_codeblock_fences():
    engine = AIEngine(api_key="mock_key")
    raw = """```json
    {
      "selected_links": [
        {"url": "https://example.com/team", "reason": "Leadership team"}
      ]
    }
    ```"""
    parsed = engine._parse_link_selection_json(raw, [])
    assert len(parsed) == 1
    assert parsed[0]["url"] == "https://example.com/team"


def test_parse_link_selection_json_fallback_on_corrupted_json():
    engine = AIEngine(api_key="mock_key")
    candidates = [
        "https://example.com/terms",
        "https://example.com/about-us",
        "https://example.com/pricing",
    ]
    parsed = engine._parse_link_selection_json("Not a json at all", candidates)
    assert len(parsed) >= 1
    # Fallback should prioritize 'about-us' or 'pricing' over 'terms'
    assert any("about-us" in p["url"] for p in parsed)


@pytest.mark.asyncio
async def test_select_relevant_links_with_mocked_gemini():
    engine = AIEngine(api_key="AIzaFakeKeyForTesting123456")

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "selected_links": [
            {"url": "https://example.com/solutions", "reason": "Deep dive into products"}
        ]
    })

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    engine.client = mock_client

    links = await engine.select_relevant_links(
        landing_url="https://example.com",
        landing_text="Landing text",
        candidate_links=["https://example.com/solutions", "https://example.com/terms"],
        max_selection=2
    )

    assert len(links) == 1
    assert links[0]["url"] == "https://example.com/solutions"
    mock_client.aio.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_brochure_stream_with_mocked_gemini():
    engine = AIEngine(api_key="AIzaFakeKeyForTesting123456")

    class MockChunk:
        def __init__(self, text):
            self.text = text

    async def mock_stream_generator(*args, **kwargs):
        chunks = [
            MockChunk("# Acme Corp\n\n"),
            MockChunk("We deliver revolutionary AI solutions.\n\n"),
            MockChunk("## Products\n- Model A\n- Model B"),
        ]
        for c in chunks:
            yield c

    mock_client = MagicMock()
    mock_client.aio.models.generate_content_stream = mock_stream_generator
    engine.client = mock_client

    collected = []
    async for chunk in engine.generate_brochure_stream(
        company_url="https://example.com",
        landing_content="Landing",
        subpages_content=[]
    ):
        collected.append(chunk)

    full_output = "".join(collected)
    assert "# Acme Corp" in full_output
    assert "revolutionary AI solutions" in full_output


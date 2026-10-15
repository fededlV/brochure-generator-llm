import json
import logging
import re
from typing import AsyncGenerator, Dict, List, Optional
from google import genai
from google.genai import types

from backend.config import settings
from backend.services.prompts import (
    LINK_SELECTION_SYSTEM_PROMPT,
    build_link_selection_user_prompt,
    build_brochure_system_prompt,
    build_brochure_user_prompt,
)

logger = logging.getLogger(__name__)


class AIEngine:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.effective_api_key
        self.model = model or settings.gemini_model
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise ValueError(
                "Gemini API key is not configured. Please provide GEMINI_API_KEY or GOOGLE_API_KEY in .env"
            )
        self._client = genai.Client(api_key=self.api_key)
        return self._client

    @client.setter
    def client(self, value: genai.Client):
        self._client = value

    async def select_relevant_links(
        self,
        landing_url: str,
        landing_text: str,
        candidate_links: List[str],
        max_selection: int = 4
    ) -> List[Dict[str, str]]:
        """
        Analyze candidate links from a landing page using Gemini and return
        the most relevant subpages for the brochure.
        """
        if not candidate_links:
            return []

        user_prompt = build_link_selection_user_prompt(
            landing_url=landing_url,
            landing_text=landing_text,
            candidate_links=candidate_links,
            max_selection=max_selection
        )

        config = types.GenerateContentConfig(
            system_instruction=LINK_SELECTION_SYSTEM_PROMPT,
            temperature=0.2,
            response_mime_type="application/json"
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config
            )
            raw_text = response.text or ""
            return self._parse_link_selection_json(raw_text, candidate_links)
        except Exception as exc:
            logger.error("Error in select_relevant_links: %s", exc)
            # Safe heuristic fallback if AI call fails or key is missing
            return self._fallback_link_selection(candidate_links, max_selection)

    def _parse_link_selection_json(self, raw_text: str, candidate_links: List[str]) -> List[Dict[str, str]]:
        """
        Robust JSON extractor for Gemini's link selection response.
        """
        cleaned = raw_text.strip()
        # Remove markdown fences if model included them
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)

        try:
            data = json.loads(cleaned)
            if isinstance(data, dict) and "selected_links" in data:
                links = data["selected_links"]
            elif isinstance(data, list):
                links = data
            else:
                links = []

            results = []
            for item in links:
                if isinstance(item, dict) and "url" in item:
                    u = item["url"].strip()
                    r = item.get("reason", "Relevant company content")
                    results.append({"url": u, "reason": r})
                elif isinstance(item, str):
                    results.append({"url": item.strip(), "reason": "Relevant company page"})
            return results
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from model output: %s", raw_text)
            return self._fallback_link_selection(candidate_links, 4)

    def _fallback_link_selection(self, candidate_links: List[str], max_selection: int) -> List[Dict[str, str]]:
        """
        Keyword-based heuristic fallback if LLM selection is unavailable.
        """
        priority_keywords = ["about", "product", "pricing", "company", "career", "solution", "team"]
        chosen = []
        for kw in priority_keywords:
            for link in candidate_links:
                if kw in link.lower() and not any(c["url"] == link for c in chosen):
                    chosen.append({"url": link, "reason": f"Matched priority keyword '{kw}'"})
                    if len(chosen) >= max_selection:
                        return chosen
        return chosen

    async def generate_brochure_stream(
        self,
        company_url: str,
        landing_content: str,
        subpages_content: List[Dict[str, str]],
        audience: str = "general",
        tone: str = "professional"
    ) -> AsyncGenerator[str, None]:
        """
        Stream the final brochure Markdown synthesis token by token from Gemini.
        """
        system_instruction = build_brochure_system_prompt(audience=audience, tone=tone)
        user_prompt = build_brochure_user_prompt(
            company_url=company_url,
            landing_content=landing_content,
            subpages_content=subpages_content
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )

        try:
            stream_or_coro = self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=user_prompt,
                config=config
            )
            # Handle whether the SDK returns an AsyncIterator directly or via coroutine
            if hasattr(stream_or_coro, "__await__"):
                response_stream = await stream_or_coro
            else:
                response_stream = stream_or_coro

            async for chunk in response_stream: # type: ignore
                if chunk.text:
                    yield chunk.text
        except Exception as exc:
            logger.error("Error generating brochure stream: %s", exc)
            raise


ai_engine = AIEngine()

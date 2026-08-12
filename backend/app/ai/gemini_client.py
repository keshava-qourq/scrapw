import json
from typing import Any

import httpx

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_GENERATE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiClient:
    """
    Thin wrapper around Gemini's structured-output REST API. Every caller
    gets back either a parsed dict or None — never an exception — so a
    Gemini outage degrades the caller's feature rather than breaking it.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def enabled(self) -> bool:
        return bool(self._settings.gemini_api_key)

    async def generate_json(
        self,
        *,
        system_prompt: str,
        user_text: str,
        response_schema: dict[str, Any],
        temperature: float = 0,
        thinking_budget: int = 100,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        url = _GENERATE_URL.format(model=self._settings.gemini_model)
        body = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_text}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": response_schema,
                "temperature": temperature,
                # A small thinking budget keeps latency reasonable for a simple
                # extraction task; Gemini's default can push well past a search
                # request's acceptable response time.
                "thinkingConfig": {"thinkingBudget": thinking_budget},
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.gemini_timeout_seconds) as client:
                response = await client.post(url, params={"key": self._settings.gemini_api_key}, json=body)
                response.raise_for_status()
                payload = response.json()
                text = payload["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
            logger.warning("gemini_request_failed", error=str(exc), user_text=user_text)
            return None

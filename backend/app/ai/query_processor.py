import re

from app.ai.gemini_client import GeminiClient
from app.core.config import Settings
from app.schemas.live_search import ParsedQuery

_SYSTEM_PROMPT = (
    "You turn a shopper's natural-language product search into structured search intent. "
    "Extract only what the text actually states — never invent a brand, category, or price that "
    "isn't written. `keywords` should be the core product terms (brand, product type, notable "
    "attributes) suitable for a text search, with price/rating phrases stripped out. Omit "
    "`brand`, `category`, `min_price`, `max_price` entirely if the text doesn't state them.\n\n"
    'Example — "Show me Samsung 55 inch 4K TVs under 50000" should produce '
    '{"keywords": ["Samsung", "55 inch", "4K", "TV"], "brand": "Samsung", "category": '
    '"television", "max_price": 50000}.'
)

_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
        "brand": {"type": "STRING"},
        "category": {"type": "STRING"},
        "min_price": {"type": "NUMBER"},
        "max_price": {"type": "NUMBER"},
    },
    "required": ["keywords"],
}

_WORD_RE = re.compile(r"[a-zA-Z0-9]+")


def _keyword_fallback(raw_query: str) -> ParsedQuery:
    """Naive fallback used when Gemini is unset or fails: just the raw
    query's words, no structured extraction. Keeps search working without AI."""
    return ParsedQuery(keywords=_WORD_RE.findall(raw_query))


class GeminiQueryProcessor:
    """
    Converts a natural-language query into `ParsedQuery` search intent.
    Falls back to basic keyword parsing on any Gemini failure — a failed
    query-understanding call never fails the search itself.
    """

    def __init__(self, settings: Settings):
        self._client = GeminiClient(settings)

    async def parse(self, raw_query: str) -> ParsedQuery:
        data = await self._client.generate_json(
            system_prompt=_SYSTEM_PROMPT,
            user_text=raw_query,
            response_schema=_RESPONSE_SCHEMA,
        )
        if data is None:
            return _keyword_fallback(raw_query)

        keywords = data.get("keywords")
        if not isinstance(keywords, list) or not keywords:
            keywords = _WORD_RE.findall(raw_query)

        return ParsedQuery(
            keywords=[str(k) for k in keywords],
            brand=data.get("brand"),
            category=data.get("category"),
            min_price=data.get("min_price"),
            max_price=data.get("max_price"),
        )

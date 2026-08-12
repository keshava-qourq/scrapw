from app.ai.gemini_client import GeminiClient
from app.connectors.registry import SUPPORTED_MARKETPLACES
from app.core.config import Settings
from app.schemas.search import ProductSearchFilters, SortOption

_SYSTEM_PROMPT = (
    "You turn a shopper's free-text product search into structured filters for exact-match "
    "backend fields. Omit a key entirely (do not include it in the JSON object, and never emit "
    "the string \"null\") unless the text explicitly states that value — an exact-match filter "
    "that doesn't match the catalog's exact spelling returns zero results instead of degrading "
    "gracefully, so a wrong guess is worse than leaving the field out. In particular: only "
    f"include `marketplace` if one of {list(SUPPORTED_MARKETPLACES)} is named literally in the "
    "text; only include `brand` if a specific brand name is stated, capitalized normally (e.g. "
    "'Nike', not 'nike'); only include `min_price`/`max_price`/`min_rating`/`min_discount` if the "
    "text gives that exact number or threshold. Do not infer typical price ranges, typical "
    "ratings, or a likely marketplace from context — if it isn't written in the query, omit the "
    "key.\n\n"
    "Example — input \"running shoes rated above 4.5\" should produce exactly "
    '{"query": "running shoes", "min_rating": 4.5} — nothing else.\n\n'
    "`query` itself should be a short plain-text product description suitable for full-text "
    "search, with the price/rating/marketplace phrases stripped out."
)

_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "query": {"type": "STRING"},
        "marketplace": {"type": "STRING", "enum": [*SUPPORTED_MARKETPLACES]},
        "brand": {"type": "STRING"},
        "min_price": {"type": "NUMBER"},
        "max_price": {"type": "NUMBER"},
        "min_rating": {"type": "NUMBER"},
        "min_discount": {"type": "NUMBER"},
        "sort": {"type": "STRING", "enum": [o.value for o in SortOption]},
    },
    "required": ["query"],
}


class QueryUnderstandingService:
    """
    Turns a natural-language search into `ProductSearchFilters` via Gemini's
    structured output. Never blocks or breaks search: any missing key,
    network failure, or malformed response falls back to treating the raw
    input as a plain query with no extra filters.
    """

    def __init__(self, settings: Settings):
        self._client = GeminiClient(settings)

    @property
    def enabled(self) -> bool:
        return self._client.enabled

    async def parse(
        self,
        raw_query: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> ProductSearchFilters:
        fallback = ProductSearchFilters(query=raw_query, page=page, page_size=page_size)

        parsed = await self._client.generate_json(
            system_prompt=_SYSTEM_PROMPT,
            user_text=raw_query,
            response_schema=_RESPONSE_SCHEMA,
        )
        if parsed is None:
            return fallback

        def clean_str(value: object) -> str | None:
            if not isinstance(value, str) or not value or value.lower() == "null":
                return None
            return value

        sort = parsed.get("sort")
        return ProductSearchFilters(
            query=clean_str(parsed.get("query")) or raw_query,
            marketplace=clean_str(parsed.get("marketplace")),
            brand=clean_str(parsed.get("brand")),
            min_price=parsed.get("min_price"),
            max_price=parsed.get("max_price"),
            min_rating=parsed.get("min_rating"),
            min_discount=parsed.get("min_discount"),
            sort=SortOption(sort) if sort in {o.value for o in SortOption} else SortOption.RELEVANCE,
            page=page,
            page_size=page_size,
        )

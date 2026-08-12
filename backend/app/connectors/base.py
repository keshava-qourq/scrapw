from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConnectorConfig:
    """Conservative, per-marketplace rate-limit and retry configuration.

    Every connector must respect these limits. Do not raise the defaults
    without a documented reason (e.g. an official API's published quota).
    """

    marketplace_code: str
    enabled: bool = False
    api_key: str = ""
    api_secret: str = ""
    requests_per_second: float = 1.0
    max_concurrent_requests: int = 2
    timeout_seconds: float = 10.0
    retry_count: int = 3


@dataclass
class RawProduct:
    """Unnormalized product payload as returned by a connector's source
    (official API response, affiliate feed row, or mock fixture)."""

    marketplace_product_id: str
    product_url: str
    payload: dict[str, Any]


class MarketplaceConnector(ABC):
    """
    Common interface every marketplace integration implements. The rest of the
    application (services, workers, API) only depends on this interface, never
    on a specific marketplace's client or response format.

    Concrete connectors must:
      - only call an official API, affiliate feed, or another mechanism the
        marketplace has explicitly permitted for this use case
      - never attempt to bypass CAPTCHA, auth, bot detection, or robots rules
      - fall back to a documented mock mode when no permitted access is
        configured, rather than fabricating data or scraping directly
    """

    def __init__(self, config: ConnectorConfig):
        self.config = config

    @property
    def marketplace_code(self) -> str:
        return self.config.marketplace_code

    @abstractmethod
    async def search_products(self, query: str, **kwargs: Any) -> list[RawProduct]:
        """Search the marketplace for products matching `query`."""

    @abstractmethod
    async def fetch_product(self, url: str) -> RawProduct | None:
        """Fetch a single product's raw data by its marketplace URL."""

    @abstractmethod
    async def fetch_product_details(self, product_id: str) -> RawProduct | None:
        """Fetch a single product's raw data by its marketplace-native product id."""

    @abstractmethod
    def normalize_product(self, raw_product: RawProduct) -> dict[str, Any]:
        """Map a RawProduct's marketplace-specific payload onto the common
        product schema fields (see app.schemas.product.ProductCreate)."""

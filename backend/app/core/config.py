from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MarketplaceSettings(BaseSettings):
    """Per-marketplace connector configuration: credentials + conservative rate limits."""

    enabled: bool = False
    api_key: str = ""
    api_secret: str = ""
    requests_per_second: float = 1.0
    max_concurrent_requests: int = 2
    timeout_seconds: float = 10.0
    retry_count: int = 3


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "product-search-engine"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/product_search"
    database_url_sync: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/product_search"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    opensearch_url: str = "http://localhost:9200"
    opensearch_username: str = ""
    opensearch_password: str = ""
    opensearch_use_ssl: bool = False
    opensearch_verify_certs: bool = False
    opensearch_product_index: str = "products"

    amazon_api_enabled: bool = False
    amazon_api_key: str = ""
    amazon_api_secret: str = ""
    amazon_partner_tag: str = ""
    amazon_region: str = "us-east-1"
    amazon_requests_per_second: float = 1.0
    amazon_max_concurrent_requests: int = 2
    amazon_timeout_seconds: float = 10.0
    amazon_retry_count: int = 3

    flipkart_api_enabled: bool = False
    flipkart_api_key: str = ""
    flipkart_api_secret: str = ""
    flipkart_requests_per_second: float = 1.0
    flipkart_max_concurrent_requests: int = 2
    flipkart_timeout_seconds: float = 10.0
    flipkart_retry_count: int = 3

    ajio_api_enabled: bool = False
    ajio_api_key: str = ""
    ajio_api_secret: str = ""
    ajio_requests_per_second: float = 1.0
    ajio_max_concurrent_requests: int = 2
    ajio_timeout_seconds: float = 10.0
    ajio_retry_count: int = 3

    myntra_api_enabled: bool = False
    myntra_api_key: str = ""
    myntra_api_secret: str = ""
    myntra_requests_per_second: float = 1.0
    myntra_max_concurrent_requests: int = 2
    myntra_timeout_seconds: float = 10.0
    myntra_retry_count: int = 3

    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    gemini_timeout_seconds: float = 10.0

    serpapi_api_key: str = ""
    serpapi_engine: str = "google_shopping"
    serpapi_timeout_seconds: float = 15.0

    search_cache_ttl_seconds: int = 900
    search_rate_limit: str = "30/minute"
    max_concurrent_providers: int = 4

    def marketplace_settings(self, marketplace: str) -> MarketplaceSettings:
        prefix = marketplace.lower()
        return MarketplaceSettings(
            enabled=getattr(self, f"{prefix}_api_enabled"),
            api_key=getattr(self, f"{prefix}_api_key"),
            api_secret=getattr(self, f"{prefix}_api_secret"),
            requests_per_second=getattr(self, f"{prefix}_requests_per_second"),
            max_concurrent_requests=getattr(self, f"{prefix}_max_concurrent_requests"),
            timeout_seconds=getattr(self, f"{prefix}_timeout_seconds"),
            retry_count=getattr(self, f"{prefix}_retry_count"),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

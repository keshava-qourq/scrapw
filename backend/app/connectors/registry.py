from app.connectors.ajio.connector import AjioConnector
from app.connectors.amazon.connector import AmazonConnector
from app.connectors.base import ConnectorConfig, MarketplaceConnector
from app.connectors.flipkart.connector import FlipkartConnector
from app.connectors.myntra.connector import MyntraConnector
from app.core.config import Settings

_CONNECTOR_CLASSES: dict[str, type[MarketplaceConnector]] = {
    "amazon": AmazonConnector,
    "flipkart": FlipkartConnector,
    "ajio": AjioConnector,
    "myntra": MyntraConnector,
}

SUPPORTED_MARKETPLACES = tuple(_CONNECTOR_CLASSES.keys())


def build_connector(marketplace_code: str, settings: Settings) -> MarketplaceConnector:
    """Factory for marketplace connectors. This is the single place in the app
    that maps a marketplace code to a concrete connector class — no other
    module should import a marketplace-specific connector directly."""
    connector_cls = _CONNECTOR_CLASSES.get(marketplace_code)
    if connector_cls is None:
        raise ValueError(f"Unsupported marketplace: {marketplace_code}")

    marketplace_settings = settings.marketplace_settings(marketplace_code)
    config = ConnectorConfig(
        marketplace_code=marketplace_code,
        enabled=marketplace_settings.enabled,
        api_key=marketplace_settings.api_key,
        api_secret=marketplace_settings.api_secret,
        requests_per_second=marketplace_settings.requests_per_second,
        max_concurrent_requests=marketplace_settings.max_concurrent_requests,
        timeout_seconds=marketplace_settings.timeout_seconds,
        retry_count=marketplace_settings.retry_count,
    )
    return connector_cls(config)

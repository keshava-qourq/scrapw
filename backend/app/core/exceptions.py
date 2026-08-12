class AppError(Exception):
    """Base application error."""


class NotFoundError(AppError):
    """Requested resource does not exist."""


class ValidationError(AppError):
    """Input failed domain validation."""


class MarketplaceError(AppError):
    """Base error for marketplace connector failures."""

    def __init__(self, marketplace: str, message: str):
        self.marketplace = marketplace
        super().__init__(f"[{marketplace}] {message}")


class MarketplaceTimeoutError(MarketplaceError):
    """Marketplace request exceeded the configured timeout."""


class MarketplaceRateLimitError(MarketplaceError):
    """Marketplace signaled that the rate limit was exceeded."""


class MarketplaceNotConfiguredError(MarketplaceError):
    """Marketplace connector has no credentials/API access configured."""


class SearchIndexError(AppError):
    """Search backend operation failed."""

import logging
import re
import sys

import structlog

from app.core.config import get_settings

_SENSITIVE_KEYS = {"api_key", "api_secret", "password", "secret", "token", "authorization"}

# Credentials passed as URL query params (e.g. `?api_key=...`) that end up inside logged strings,
# typically an exception message quoting the request URL.
_SECRET_QUERY_PARAM = re.compile(r"([?&](?:api_key|key|token|access_token)=)[^&\s'\"]+", re.IGNORECASE)


def _redact_sensitive(_, __, event_dict: dict) -> dict:
    for key, value in list(event_dict.items()):
        if key.lower() in _SENSITIVE_KEYS:
            event_dict[key] = "***REDACTED***"
        elif isinstance(value, str):
            event_dict[key] = _SECRET_QUERY_PARAM.sub(r"\1***REDACTED***", value)
    return event_dict


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )
    # httpx logs every request URL at INFO, and some providers (SerpApi, Gemini) take their
    # API key as a query parameter — keep those URLs, and so the keys, out of the logs.
    for noisy_logger in ("httpx", "httpcore"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _redact_sensitive,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)

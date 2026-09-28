import logging

from app.core.logging import _redact_sensitive, configure_logging


def test_http_client_request_urls_are_not_logged():
    # Provider API keys travel as URL query params; httpx would log them at INFO.
    configure_logging()
    assert logging.getLogger("httpx").getEffectiveLevel() >= logging.WARNING
    assert logging.getLogger("httpcore").getEffectiveLevel() >= logging.WARNING


def test_secret_query_params_are_scrubbed_from_logged_strings():
    event = {
        "event": "gemini_request_failed",
        "error": "Server error '503' for url 'https://example.com/v1/generate?key=SECRET123&alt=json'",
        "detail": "GET https://serpapi.com/search?q=shoes&api_key=SECRET456",
        "api_key": "SECRET789",
    }
    redacted = _redact_sensitive(None, None, event)
    rendered = str(redacted)
    for secret in ("SECRET123", "SECRET456", "SECRET789"):
        assert secret not in rendered
    assert "&alt=json" in redacted["error"]
    assert "q=shoes" in redacted["detail"]

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.deps import get_search_index
from app.api.v1 import cards, categories, health, live_search, marketplaces, products, watchlist
from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError, SearchIndexError, ValidationError
from app.core.logging import configure_logging, get_logger
from app.core.rate_limit import limiter

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    search_index = get_search_index()
    try:
        await search_index.ensure_index()
    except Exception:  # noqa: BLE001
        logger.warning("search_index_unavailable_at_startup")
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(SearchIndexError)
async def search_index_error_handler(request: Request, exc: SearchIndexError) -> JSONResponse:
    logger.error("search_index_error", error=str(exc))
    return JSONResponse(status_code=503, content={"detail": "Search backend unavailable"})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.error("unhandled_app_error", error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal error"})


app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(products.router, prefix=settings.api_v1_prefix)
app.include_router(marketplaces.router, prefix=settings.api_v1_prefix)
app.include_router(categories.router, prefix=settings.api_v1_prefix)
app.include_router(watchlist.router, prefix=settings.api_v1_prefix)
app.include_router(live_search.router, prefix=settings.api_v1_prefix)
app.include_router(cards.router, prefix=settings.api_v1_prefix)

"""FastAPI entrypoint for local RAG backend."""

from __future__ import annotations

from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.shared.config import SETTINGS
from app.shared.logging_utils import configure_logging, get_logger

configure_logging(SETTINGS.logs_dir)
logger = get_logger(__name__)

app = FastAPI(title="Local RAG API", version="0.1.0")

cors_origins = [origin.strip() for origin in SETTINGS.api_cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    started = perf_counter()
    logger.info("request start method=%s path=%s", request.method, request.url.path)
    response = await call_next(request)
    logger.info(
        "request end method=%s path=%s status=%s elapsed_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        int((perf_counter() - started) * 1000),
    )
    return response


app.include_router(router)

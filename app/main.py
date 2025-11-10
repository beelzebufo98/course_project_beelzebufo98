import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.errors import ApiError
from app.init_db import init_db
from app.limiter import limiter
from app.logging_filters import SecretMaskingFilter
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.routers import internal_categories, users, wishes

logging.getLogger().addFilter(SecretMaskingFilter())
app = FastAPI(title="SecDev Course App", version="0.1.0")
app.state.limiter = limiter
app.add_middleware(SecurityHeadersMiddleware)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    logging.warning(f"[{exc.correlation_id}] {exc.code}: {exc.message}")
    return exc.to_json()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "http_error",
            "title": "HTTP Error",
            "status": exc.status_code,
            "detail": detail,
        },
        media_type="application/problem+json",
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "type": "rate_limit_exceeded",
            "title": "Too Many Requests",
            "status": 429,
            "detail": f"Rate limit exceeded: {exc.detail}",
        },
        media_type="application/problem+json",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(users.router)
app.include_router(wishes.router)
app.include_router(internal_categories.router)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.errors import ApiError
from app.init_db import init_db
from app.limiter import limiter
from app.routers import internal_categories, users, wishes

app = FastAPI(title="SecDev Course App", version="0.1.0")
app.state.limiter = limiter


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
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


_DB = {"items": []}


@app.post("/items")
def create_item(name: str):
    if not name or len(name) > 100:
        raise ApiError(
            code="validation_error", message="name must be 1..100 chars", status=422
        )
    item = {"id": len(_DB["items"]) + 1, "name": name}
    _DB["items"].append(item)
    return item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    for it in _DB["items"]:
        if it["id"] == item_id:
            return it
    raise ApiError(code="not_found", message="item not found", status=404)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(users.router)
app.include_router(wishes.router)
app.include_router(internal_categories.router)

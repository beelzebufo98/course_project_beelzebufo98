from uuid import uuid4

from fastapi.responses import JSONResponse


class ApiError(Exception):

    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status
        self.correlation_id = str(uuid4())

    def to_json(self) -> JSONResponse:
        payload = {
            "type": self.code,
            "title": self.code.replace("_", " ").capitalize(),
            "status": self.status,
            "detail": self.message,
            "correlation_id": self.correlation_id,
        }
        response = JSONResponse(
            status_code=self.status,
            content=payload,
            media_type="application/problem+json",
        )
        response.headers["X-Correlation-Id"] = self.correlation_id
        return response


class ValidationError(ApiError):
    def __init__(self, message: str = "validation failed"):
        super().__init__("validation_error", message, 422)


class NotFoundError(ApiError):
    def __init__(self, message: str = "resource not found"):
        super().__init__("not_found", message, 404)


class ConflictError(ApiError):
    def __init__(self, message: str = "conflict"):
        super().__init__("conflict", message, 409)

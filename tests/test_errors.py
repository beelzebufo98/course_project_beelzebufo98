from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert body["type"] == "not_found"


def test_validation_error():
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["type"] == "validation_error"


def test_problem_response_has_correlation_id():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert "correlation_id" in body
    assert isinstance(body["correlation_id"], str)
    assert body["type"] == "not_found"
    assert "application/problem+json" in r.headers["content-type"]
    assert "X-Correlation-Id" in r.headers

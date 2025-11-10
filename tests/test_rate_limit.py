import time

import pytest

from app.limiter import limiter


def test_user_create_rate_limit(client):
    data = {"username": "u", "first_name": "f", "last_name": "l"}

    for i in range(5):
        r = client.post("/users", json={**data, "username": f"user{i}"})
        assert r.status_code in (201, 429)

    r = client.post("/users", json={**data, "username": "overflow"})
    assert r.status_code == 429
    body = r.json()
    assert body["status"] == 429
    assert "Too Many" in body["title"]
    assert "rate limit" in body["detail"].lower()


def test_wish_create_rate_limit(client, test_user):
    wish = {
        "title": "Test wish",
        "link": "https://example.com",
        "price_estimate": 42.0,
        "notes": "rate limit test",
    }

    for i in range(10):
        r = client.post("/wishes", json={**wish, "title": f"wish{i}"})
        assert r.status_code in (201, 429)

    r = client.post("/wishes", json={**wish, "title": "overflow"})
    assert r.status_code == 429
    body = r.json()
    assert body["status"] == 429
    assert "Too Many" in body["title"]


@pytest.fixture
def sample_wish(client, test_user):
    storage = limiter._storage
    if hasattr(storage, "_storage"):
        storage._storage.clear()

    time.sleep(1)

    resp = client.post(
        "/wishes",
        json={
            "title": "Sample wish",
            "link": "https://example.com",
            "price_estimate": 1.0,
            "notes": "test",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_get_wish_rate_limit(client, sample_wish):
    wid = sample_wish["id"]

    for i in range(30):
        r = client.get(f"/wishes/{wid}")
        assert r.status_code in (200, 429)

    r = client.get(f"/wishes/{wid}")
    assert r.status_code == 429
    body = r.json()
    assert body["status"] == 429
    assert "rate limit" in body["detail"].lower()

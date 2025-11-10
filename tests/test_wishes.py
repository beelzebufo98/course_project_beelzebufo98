import time
import uuid

import pytest


@pytest.fixture
def category(client):
    r = client.post(
        "/internal/categories", json={"name": f"TestCat_{uuid.uuid4().hex[:6]}"}
    )
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture
def wish_payload(category, test_user):
    return {
        "title": f"Wish {uuid.uuid4().hex[:6]}",
        "link": "https://example.com",
        "price_estimate": 1000.0,
        "notes": "test notes",
        "is_fulfilled": False,
        "category_id": category["id"],
        "owner_id": test_user.id,
    }


def test_create_wish(client, wish_payload, test_user):
    r = client.post("/wishes", json=wish_payload)
    assert r.status_code == 201, r.text
    data = r.json()

    assert data["title"] == wish_payload["title"]
    assert data["link"] == wish_payload["link"]
    assert float(data["price_estimate"]) == float(wish_payload["price_estimate"])
    assert data["notes"] == wish_payload["notes"]
    assert data["is_fulfilled"] is False
    assert "id" in data


def test_get_wish(client, wish_payload, test_user):
    time.sleep(1)
    r = client.post("/wishes", json=wish_payload)
    assert r.status_code == 201, r.text
    wid = r.json()["id"]

    r2 = client.get(f"/wishes/{wid}")
    assert r2.status_code == 200, r2.text
    data = r2.json()

    assert data["id"] == wid
    assert data["title"] == wish_payload["title"]
    assert data["is_fulfilled"] is False


def test_update_wish_title_only(client, wish_payload, test_user):
    r = client.post("/wishes", json=wish_payload)
    assert r.status_code == 201, r.text
    wid = r.json()["id"]

    r2 = client.patch(f"/wishes/{wid}", json={"title": "Updated Title"})
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data["title"] == "Updated Title"
    assert data["is_fulfilled"] is False


def test_update_wish_price_invalid(client, wish_payload, test_user):
    r = client.post("/wishes", json=wish_payload)
    wid = r.json()["id"]

    r2 = client.patch(f"/wishes/{wid}", json={"price_estimate": "abc"})
    assert r2.status_code == 422, r2.text


def test_update_wish_not_found(client):
    r = client.patch("/wishes/999999", json={"title": "X"})
    assert r.status_code == 404, r.text
    body = r.json()

    assert body["type"] == "not_found"
    assert "detail" in body

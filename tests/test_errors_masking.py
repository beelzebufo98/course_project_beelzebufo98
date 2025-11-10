def test_wish_create_invalid_owner_masks_sql_and_has_correlation_id(client, test_user):
    payload = {
        "title": "LeakTest",
        "link": "https://example.com",
        "price_estimate": 10.0,
        "notes": "bad fk",
        "is_fulfilled": False,
        "category_id": None,
        "owner_id": 999999,
    }
    r = client.post("/wishes", json=payload)
    assert r.status_code == 422
    j = r.json()

    assert j["type"] == "validation_error"
    assert j["status"] == 422
    assert "несуществующий" in j["detail"]

    leaked = ["psycopg2", "SELECT", "INSERT", "constraint", "wishes_owner_id_fkey"]
    assert not any(tok.lower() in j["detail"].lower() for tok in leaked)

    cid_body = j.get("correlation_id")
    cid_header = r.headers.get("X-Correlation-Id")
    assert cid_body and cid_header and cid_body == cid_header


def test_user_duplicate_masks_sql_and_has_correlation_id(client):
    user = {"username": "dup_user", "first_name": "A", "last_name": "B"}
    r1 = client.post("/users", json=user)
    assert r1.status_code == 201

    r2 = client.post("/users", json=user)
    assert r2.status_code == 422
    j = r2.json()

    assert j["type"] == "validation_error"
    assert "существует" in j["detail"]

    leaked = [
        "psycopg2",
        "duplicate key",
        "unique constraint",
        "INSERT",
        "users_username_key",
    ]
    assert not any(tok.lower() in j["detail"].lower() for tok in leaked)

    cid_body = j.get("correlation_id")
    cid_header = r2.headers.get("X-Correlation-Id")
    assert cid_body and cid_header and cid_body == cid_header

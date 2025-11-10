import uuid


def test_create_and_get_user(client):
    name = f"user_{uuid.uuid4().hex[:8]}"
    first_name = "First"
    last_name = "Last"

    r = client.post(
        "/users",
        json={"username": name, "first_name": first_name, "last_name": last_name},
    )
    assert r.status_code == 201, r.text
    user_id = r.json()["id"]

    r2 = client.get(f"/users/{user_id}")
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["username"] == name
    assert body["first_name"] == first_name
    assert body["last_name"] == last_name


def test_user_not_found(client):
    r = client.get("/users/1111111111")
    assert r.status_code == 404
    body = r.json()
    assert body["type"] == "not_found"

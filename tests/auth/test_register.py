def test_register_creates_user_with_customer_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "supersecret"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["role"]["name"] == "customer"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_rejects_duplicate_email(client):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "supersecret"}
    client.post("/api/v1/auth/register", json=payload)

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_register_treats_email_case_as_duplicate(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Bob", "email": "Bob@Example.com", "password": "supersecret"},
    )

    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Bob Again", "email": "bob@example.com", "password": "supersecret"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_register_rejects_password_shorter_than_8_chars(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Carol", "email": "carol@example.com", "password": "short"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

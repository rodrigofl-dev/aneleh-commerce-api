def test_me_without_token_returns_401(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_me_returns_all_expected_fields(client, register_and_get_token):
    token = register_and_get_token("testuser@example.com")

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    
    expected_fields = ["id", "name", "email", "role", "created_at", "updated_at"]
    for field in expected_fields:
        assert field in body

    assert body["name"] == "Test User"
    assert body["email"] == "testuser@example.com"
    assert body["role"]["name"] == "customer"
    assert "password" not in body
    assert "password_hash" not in body

def test_me_duplicate_email(client, register_and_get_token):
    register_and_get_token("bob@example.com")
    token = register_and_get_token("jake@example.com")

    response = client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "bob@example.com"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_me_update_name(client, register_and_get_token):
    token = register_and_get_token("jake@example.com")

    response = client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Jakezinho"},
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Jakezinho"


def test_me_update_email(client, register_and_get_token):
    token = register_and_get_token("jake@example.com")

    response = client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "new_jake@example.com"},
    )
    
    assert response.status_code == 200
    assert response.json()["email"] == "new_jake@example.com"


def test_me_update_password_allows_login_with_new_password(client, register_and_get_token):
    token = register_and_get_token("jake@example.com")

    response = client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "123"},
    )
    
    assert response.status_code == 200
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "jake@example.com", "password": "123"},
    )
    assert login_response.status_code == 200


def test_me_update_password_revokes_current_token(client, register_and_get_token):
    token = register_and_get_token("jake@example.com")

    client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "123"},
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_REVOKED"

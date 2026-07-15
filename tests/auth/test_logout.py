from app.core.token_blacklist import is_token_blacklisted


def test_logout_blacklists_the_token(client, register_and_get_token):
    token = register_and_get_token("dave@example.com")

    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert is_token_blacklisted(token) is True


def test_blacklisted_token_is_rejected_on_protected_endpoint(
    client, register_and_get_token
):
    token = register_and_get_token("erin@example.com")
    client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})

    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_REVOKED"


def test_logout_without_token_returns_401(client):
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

def test_login(client, register_and_get_token):
    register_and_get_token("testuser@example.com")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "supersecret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert body["user"]["email"] == "testuser@example.com"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_login_credentials(client, register_and_get_token):
    register_and_get_token("testuser@example.com")

    wrongpass_response = client.post(
        "/api/v1/auth/login",
        json={"email": "testuser@example.com", "password": "wrong"},
    )

    wrongemail_response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "supersecret"},
    )

    assert wrongpass_response.status_code == 401
    assert wrongemail_response.status_code == 401
    assert (
        wrongpass_response.json()["error"]["code"]
        == wrongemail_response.json()["error"]["code"]
        == "INVALID_CREDENTIALS"
    )


def test_login_treats_email_case(client, register_and_get_token):
    register_and_get_token("testuser@example.com")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "TESTUSER@example.com", "password": "supersecret"},
    )

    assert response.status_code == 200

def test_userid_without_token_returns_401(client):
    response = client.get("/api/v1/users/1")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_userid_returns_all_expected_fields(
    client, register_and_get_token, get_user_by_email
):
    admin_token = register_and_get_token("apoc@example.com", role="admin")
    apoc = get_user_by_email("apoc@example.com")
    response = client.get(
        f"/api/v1/users/{apoc.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    body = response.json()

    expected_fields = ["id", "name", "email", "role", "created_at", "updated_at"]
    for field in expected_fields:
        assert field in body

    assert body["name"] == "Test User"
    assert body["email"] == "apoc@example.com"
    assert body["role"]["name"] == "admin"
    assert "password" not in body
    assert "password_hash" not in body


def test_get_user_by_id_as_admin_returns_another_users_data(
    client, register_and_get_token, get_user_by_email
):
    admin_token = register_and_get_token("apoc@example.com", role="admin")
    register_and_get_token("neo@example.com")

    neo = get_user_by_email("neo@example.com")

    response = client.get(
        f"/api/v1/users/{neo.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "neo@example.com"


def test_get_user_by_id_forbidden_for_customer(client, register_and_get_token):
    customer_token = register_and_get_token("neo@example.com")

    response = client.get(
        "/api/v1/users/1",
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_get_user_by_id_not_found(client, register_and_get_token):
    admin_token = register_and_get_token("apoc@example.com", role="admin")

    response = client.get(
        "/api/v1/users/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_update_role_forbidden_for_customer(
    client, register_and_get_token, get_user_by_email
):
    customer_token = register_and_get_token("apoc@example.com")
    apoc = get_user_by_email("apoc@example.com")

    response = client.patch(
        f"/api/v1/users/{apoc.id}/role",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"role": "admin"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_admin_can_be_demoted_when_not_the_last_one(
    client, register_and_get_token, get_user_by_email
):
    admin_token = register_and_get_token("apoc@example.com", role="admin")
    register_and_get_token("neo@example.com", role="admin")

    neo = get_user_by_email("neo@example.com")

    response = client.patch(
        f"/api/v1/users/{neo.id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "customer"},
    )

    assert response.status_code == 200
    assert response.json()["role"]["name"] == "customer"


def test_last_admin_cannot_be_demoted(
    client, register_and_get_token, get_user_by_email
):
    admin_token = register_and_get_token("apoc@example.com", role="admin")
    apoc = get_user_by_email("apoc@example.com")

    response = client.patch(
        f"/api/v1/users/{apoc.id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "customer"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "LAST_ADMIN_CANNOT_BE_DEMOTED"

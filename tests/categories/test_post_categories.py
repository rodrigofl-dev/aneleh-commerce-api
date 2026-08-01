def test_create_category(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create category
    response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Electronics"

    # Test duplicate name
    response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CATEGORY_ALREADY_EXISTS"


def test_admin_only(client, register_and_get_token):
    token = register_and_get_token("notadmin@example.com")

    # Create category as non-admin
    response = client.post(
        "/api/v1/categories",
        json={"name": "Sports"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"

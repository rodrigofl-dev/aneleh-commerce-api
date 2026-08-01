def test_admin_only(client, register_and_get_token):
    admintoken = register_and_get_token("admin@example.com", role="admin")
    token = register_and_get_token("notadmin@example.com")

    # Create a category
    response = client.post(
        "/api/v1/categories",
        json={"name": "Home"},
        headers={"Authorization": f"Bearer {admintoken}"}
    )

    assert response.status_code == 201
    category_id = response.json()["id"]
    
    # Update category as non-admin
    response = client.patch(
        f"/api/v1/categories/{category_id}",
        json={"name": "Home & Garden"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_update_category(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")
    
    # Create a category
    response = client.post(
        "/api/v1/categories",
        json={"name": "Home"},
        headers={"Authorization": f"Bearer {token}"}
    )
    category_id = response.json()["id"]

    duplicate_response = client.post(
        "/api/v1/categories",
        json={"name": "Eletronics"},
        headers={"Authorization": f"Bearer {token}"}
    )
    duplicate_category_id = duplicate_response.json()["id"]
    
    # Update category
    response = client.patch(
        f"/api/v1/categories/{category_id}",
        json={"name": "Home & Garden"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Home & Garden"

    # Test duplicate name
    duplicate_response = client.patch(
        f"/api/v1/categories/{duplicate_category_id}",
        json={"name": "Home & Garden"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["error"]["code"] == "CATEGORY_ALREADY_EXISTS"

    # Test category not found
    response = client.patch(
        f"/api/v1/categories/{99}",
        json={"name": "Home"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CATEGORY_NOT_FOUND"

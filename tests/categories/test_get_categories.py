def test_get_all_categories(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create some categories
    for i in range(5):
        response = client.post(
            "/api/v1/categories",
            json={"name": f"Category {i}"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

    # Get all categories
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "limit" in response.json()
    assert "offset" in response.json()


def test_get_category_by_id(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create a category
    response = client.post(
        "/api/v1/categories",
        json={"name": "Books"},
        headers={"Authorization": f"Bearer {token}"},
    )
    category_id = response.json()["id"]

    # Get category by ID
    response = client.get(f"/api/v1/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Books"

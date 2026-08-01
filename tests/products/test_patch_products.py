def test_patch_product_with_invalid_price(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")
    
    # Create a category first
    category_response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"}
    )
    category_id = category_response.json()["id"]
    assert category_response.status_code == 201
    
    # Create a product
    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Smartphone",
            "description": "A smartphone",
            "category_id": category_id,
            "price": 699.99,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    product_id = product_response.json()["id"]
    assert product_response.status_code == 201
    
    # Test PATCH with invalid price (<= 0)
    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={"price": 0},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_patch_product_with_missing_category(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")
        
    # Create a category first
    category_response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"}
    )
    category_id = category_response.json()["id"]
    assert category_response.status_code == 201
    
    # Create a product
    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Smartphone",
            "description": "A smartphone",
            "category_id": category_id,
            "price": 699.99,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    product_id = product_response.json()["id"]
    assert product_response.status_code == 201

    # Test PATCH with invalid category ID
    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={"category_id": 55},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CATEGORY_NOT_FOUND"


def test_patch_product_not_found(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Test PATCH with non-existent product ID
    response = client.patch(
        "/api/v1/products/999",
        json={"name": "Test Product"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


def test_patch_product_success(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")
    
    # Create a category first
    category_response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"}
    )
    category_id = category_response.json()["id"]
    assert category_response.status_code == 201

    # Create a category first
    new_category_response = client.post(
        "/api/v1/categories",
        json={"name": "Good stuff"},
        headers={"Authorization": f"Bearer {token}"}
    )
    new_category_id = new_category_response.json()["id"]
    assert new_category_response.status_code == 201
    
    # Create a product
    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Smartphone",
            "description": "A smartphone",
            "category_id": category_id,
            "price": 699.99,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    product_id = product_response.json()["id"]
    assert product_response.status_code == 201

    # Test PATCH success
    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Updated Product",
            "description": "Updated description",
            "price": 200.0,
            "category_id": new_category_id,
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Updated Product"
    assert data["price"] == "200.00"
    assert data["description"] == "Updated description"
    assert data["category_id"] == new_category_id

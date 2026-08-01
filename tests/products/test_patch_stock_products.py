def test_patch_changing_stock_success(client, register_and_get_token):
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

    # Test PATCH changing stock
    response = client.patch(
        f"/api/v1/products/{product_id}/stock",
        json={
            "quantity_change": 50,
            "reason": "I bought more stuff",
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 50

    response = client.patch(
        f"/api/v1/products/{product_id}/stock",
        json={
            "quantity_change": -30,
            "reason": "Sold",
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 20


def test_patch_stock_cannot_be_negative(client, register_and_get_token):
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

    # Test PATCH changing stock
    response = client.patch(
        f"/api/v1/products/{product_id}/stock",
        json={
            "quantity_change": 50,
            "reason": "I bought more stuff",
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 50

    response = client.patch(
        f"/api/v1/products/{product_id}/stock",
        json={
            "quantity_change": -51,
            "reason": "Sold yesterday",
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STOCK_CANNOT_BE_NEGATIVE"

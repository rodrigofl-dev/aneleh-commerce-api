def test_create_product_success(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create a category first
    category_response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"},
    )
    category_id = category_response.json()["id"]

    # Create a product
    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Smartphone",
            "description": "A smartphone",
            "category_id": category_id,
            "price": 699.99,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert product_response.status_code == 201
    assert product_response.json()["name"] == "Smartphone"
    assert product_response.json()["category_id"] == category_id
    assert product_response.json()["price"] == "699.99"
    assert product_response.json()["stock_quantity"] == 0


def test_create_product_with_invalid_category(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Try to create product with invalid category
    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Smartphone",
            "description": "A smartphone",
            "category_id": 99,
            "price": 699.99,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert product_response.status_code == 404
    assert product_response.json()["error"]["code"] == "CATEGORY_NOT_FOUND"


def test_create_product_with_invalid_price(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create a category
    category_response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"},
    )
    category_id = category_response.json()["id"]

    # Try to create product with price <= 0
    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Smartphone",
            "description": "A smartphone",
            "category_id": category_id,
            "price": 0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert product_response.status_code == 422
    assert product_response.json()["error"]["code"] == "VALIDATION_ERROR"

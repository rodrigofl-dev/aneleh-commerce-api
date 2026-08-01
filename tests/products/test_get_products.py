def test_list_products(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create a category
    category_response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"},
    )
    category_id = category_response.json()["id"]

    # Create some products
    for i in range(5):
        product_response = client.post(
            "/api/v1/products",
            json={
                "name": f"Product {i}",
                "description": f"Description for product {i}",
                "category_id": category_id,
                "price": 100.00,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert product_response.status_code == 201

    # List products
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "limit" in response.json()
    assert "offset" in response.json()


def test_list_products_by_category(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create a category
    category_response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"},
    )
    category_id = category_response.json()["id"]

    # Create some products
    for i in range(5):
        product_response = client.post(
            "/api/v1/products",
            json={
                "name": f"Product {i}",
                "description": f"Description for product {i}",
                "category_id": category_id,
                "price": 100.00,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert product_response.status_code == 201

    # List products by category
    response = client.get("/api/v1/products?category_id=1")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "limit" in response.json()
    assert "offset" in response.json()


def test_list_products_by_category_and_status(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create a category
    category_response = client.post(
        "/api/v1/categories",
        json={"name": "Electronics"},
        headers={"Authorization": f"Bearer {token}"},
    )
    category_id = category_response.json()["id"]

    # Create some products
    for i in range(5):
        product_response = client.post(
            "/api/v1/products",
            json={
                "name": f"Product {i}",
                "description": f"Description for product {i}",
                "category_id": category_id,
                "price": 100.00,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert product_response.status_code == 201

    # List products by category and status
    response = client.get("/api/v1/products?category_id=1&include_unavailable=true")
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "limit" in response.json()
    assert "offset" in response.json()


def test_get_product_by_id(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")

    # Create a category
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
    product_id = product_response.json()["id"]

    # Get product by ID
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Smartphone"
    assert response.json()["category_id"] == category_id
    assert response.json()["price"] == "699.99"
    assert response.json()["stock_quantity"] == 0

def test_delete_category_success(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")
    
    # Create a category
    response = client.post(
        "/api/v1/categories",
        json={"name": "Toys"},
        headers={"Authorization": f"Bearer {token}"}
    )
    category_id = response.json()["id"]
    
    # Delete category
    response = client.delete(
        f"/api/v1/categories/{category_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204


def test_delete_category_with_products(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")
    
    # Create a category
    response = client.post(
        "/api/v1/categories",
        json={"name": "Toys"},
        headers={"Authorization": f"Bearer {token}"}
    )
    category_id = response.json()["id"]
    
    # Create a product in this category
    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Toy Car",
            "description": "A toy car",
            "category_id": category_id,
            "price": 29.99,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    product_id = product_response.json()["id"]
    
    # Try to delete category with products
    response = client.delete(
        f"/api/v1/categories/{category_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CATEGORY_HAS_PRODUCTS"

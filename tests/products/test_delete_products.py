def test_delete_success(client, register_and_get_token):
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
    assert product_response.json()["active"] == True

    # Test DELETE success
    response = client.delete(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    validation = client.get(f"/api/v1/products/{product_id}")
    assert validation.status_code == 200
    assert validation.json()["active"] == False


def test_delete_product_not_found(client, register_and_get_token):
    token = register_and_get_token("admin@example.com", role="admin")
    
    # Test DELETE success
    response = client.delete(
        f"/api/v1/products/99",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

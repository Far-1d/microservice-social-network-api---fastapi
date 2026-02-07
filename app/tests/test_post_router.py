def test_get_list_posts(client):
    response = client.get("/api/posts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # assert response.json() == None
def test_update_temperatures(api_client):
    api_client.post(
        "/cities",
        json={"name": "Berlin", "additional_info": "Germany"}
    )

    response = api_client.post("/temperatures/update")

    assert response.status_code == 200
    assert "records_created" in response.json()


def test_get_temperatures(api_client):
    response = api_client.get("/temperatures")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

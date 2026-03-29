"""API tests for health and model metadata endpoints."""


def test_health_success(client):
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["data"]["environment"] == "test"


def test_models_info_success(client):
    response = client.get("/models/info")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert len(body["data"]["models"]) == 2
    methods = {item["method"] for item in body["data"]["models"]}
    assert methods == {"nail", "conjunctiva"}

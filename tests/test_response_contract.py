"""API contract tests for response envelopes and history endpoints."""


def test_predict_nail_success_envelope(client, valid_image_bytes):
    response = client.post(
        "/predict/nail",
        data={"user_id": "user-abc"},
        files={"image": ("nail.jpg", valid_image_bytes, "image/jpeg")},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["method"] == "nail"
    assert "prediction_id" in body["data"]


def test_predict_conjunctiva_invalid_mime_error_envelope(client):
    response = client.post(
        "/predict/conjunctiva",
        data={"user_id": "user-xyz"},
        files={"image": ("bad.txt", b"not-image", "text/plain")},
    )
    assert response.status_code == 422

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_MIME_TYPE"


def test_history_list_and_detail(client, valid_image_bytes):
    create_response = client.post(
        "/predict/nail",
        data={"user_id": "history-user"},
        files={"image": ("nail.jpg", valid_image_bytes, "image/jpeg")},
    )
    assert create_response.status_code == 200

    prediction_id = create_response.json()["data"]["prediction_id"]

    list_response = client.get("/history/history-user", params={"limit": 10})
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert list_body["success"] is True
    assert len(list_body["data"]["items"]) >= 1

    detail_response = client.get(f"/history/history-user/{prediction_id}")
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["success"] is True
    assert detail_body["data"]["id"] == prediction_id


def test_request_validation_error_envelope(client):
    response = client.post("/predict/nail", data={"user_id": "u-no-file"})
    assert response.status_code == 422

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "REQUEST_VALIDATION_ERROR"

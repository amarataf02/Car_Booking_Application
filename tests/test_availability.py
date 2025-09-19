def test_availability_endpoint_excludes_booked_ids(client):
    assert client.post("/api/bookings", json={
        "car_id": 3, "start_date": "2025-08-10", "end_date": "2025-08-12"
    }).status_code == 201

    res = client.get("/api/cars/available", params={
        "start": "2025-08-10", "end": "2025-08-12"
    })
    assert res.status_code == 200, res.text
    payload = res.json()
    available_ids = {c["id"] for c in payload["cars"]}
    assert 3 not in available_ids
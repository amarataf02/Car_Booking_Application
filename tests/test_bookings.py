def detail_text(resp):
    d = resp.json().get("detail")
    if isinstance(d, str):
        return d
    if isinstance(d, dict):
        return d.get("message", "")
    return ""

def test_create_booking_by_id_success(client):
    payload = {"car_id": 1, "start_date": "2025-09-20", "end_date": "2025-09-22"}
    r = client.post("/api/bookings", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["car_id"] == 1
    assert data["days"] == 3
    assert data["total_price"] == 150.0

def test_create_booking_by_id_single_day(client):
    r = client.post("/api/bookings", json={
        "car_id": 2,
        "start_date": "2025-10-01",
        "end_date": "2025-10-01"
    })
    assert r.status_code == 201
    data = r.json()
    assert data["days"] == 1
    assert data["total_price"] == 70.0

def test_create_booking_by_id_invalid_range(client):
    r = client.post("/api/bookings", json={
        "car_id": 2,
        "start_date": "2025-10-05",
        "end_date": "2025-10-01"
    })
    assert r.status_code == 400
    assert "after" in detail_text(r).lower()

def test_create_booking_by_id_conflict_at_edge_inclusive(client):
    r1 = client.post("/api/bookings", json={
        "car_id": 1, "start_date": "2025-09-20", "end_date": "2025-09-22"
    })
    assert r1.status_code == 201

    r2 = client.post("/api/bookings", json={
        "car_id": 1, "start_date": "2025-09-22", "end_date": "2025-09-24"
    })
    assert r2.status_code == 400
    assert "already booked" in detail_text(r2).lower()

def test_create_booking_by_seats_picks_next_available(client):
    r1 = client.post("/api/bookings", json={
        "car_id": 1, "start_date": "2025-11-10", "end_date": "2025-11-12"
    })
    assert r1.status_code == 201

    r2 = client.post("/api/bookings/by-seats", json={
        "seats": 5, "start_date": "2025-11-10", "end_date": "2025-11-12"
    })
    assert r2.status_code == 201, r2.text
    data = r2.json()
    assert data["car_id"] == 2
    assert data["days"] == 3
    assert data["total_price"] == 210.0

def test_create_booking_by_seats_when_none_available(client):
    for car_id in (1, 2):
        r = client.post("/api/bookings", json={
            "car_id": car_id, "start_date": "2025-12-01", "end_date": "2025-12-03"
        })
        assert r.status_code == 201

    r2 = client.post("/api/bookings/by-seats", json={
        "seats": 5, "start_date": "2025-12-01", "end_date": "2025-12-03"
    })
    assert r2.status_code == 400
    assert "no available car" in detail_text(r2).lower()

import json
from pathlib import Path

def _read_bookings_json_text() -> str:
    p = Path("data/bookings.json")
    assert p.exists(), "bookings.json not found; fixture should have created it"
    return p.read_text(encoding="utf-8")

def test_end_to_end_create_car_and_bookings_and_persistence(client):
    # --- 1) create a brand-new car (unique seats so by-seats picks it) ---
    new_car_payload = {
        "make": "Peugeot",
        "model": "208",
        "seats": 4,
        "daily_price": 39.50,
    }
    r_car = client.post("/api/cars", json=new_car_payload)
    assert r_car.status_code == 201, r_car.text
    car = r_car.json()
    car_id = car["id"]
    daily_price = float(car["daily_price"])

    # sanity: car appears in /cars list
    r_list = client.get("/api/cars")
    assert r_list.status_code == 200
    ids = {c["id"] for c in r_list.json()}
    assert car_id in ids

    # --- 2) before any booking, it should be available for a window ---
    start1, end1 = "2025-04-10", "2025-04-12"  # inclusive -> 3 days
    r_avail_before = client.get("/api/cars/available", params={"start": start1, "end": end1})
    assert r_avail_before.status_code == 200
    avail_ids_before = {c["id"] for c in r_avail_before.json()["cars"]}
    assert car_id in avail_ids_before

    # --- 3) book by ID; verify inclusive days and total price ---
    r_book_id = client.post("/api/bookings", json={
        "car_id": car_id,
        "start_date": start1,
        "end_date": end1
    })
    assert r_book_id.status_code == 201, r_book_id.text
    b1 = r_book_id.json()
    assert b1["car_id"] == car_id
    assert b1["start_date"] == start1
    assert b1["end_date"] == end1
    assert b1["days"] == 3
    assert b1["total_price"] == round(3 * daily_price, 2)

    # now the same window should exclude this car from availability
    r_avail_after = client.get("/api/cars/available", params={"start": start1, "end": end1})
    assert r_avail_after.status_code == 200
    avail_ids_after = {c["id"] for c in r_avail_after.json()["cars"]}
    assert car_id not in avail_ids_after

    # --- 4) book by seats on a non-overlapping range; should pick the same car ---
    start2, end2 = "2025-04-14", "2025-04-15"
    r_book_seats = client.post("/api/bookings/by-seats", json={
        "seats": 4,
        "start_date": start2,
        "end_date": end2
    })
    assert r_book_seats.status_code == 201, r_book_seats.text
    b2 = r_book_seats.json()
    assert b2["car_id"] == car_id
    assert b2["days"] == 2
    assert b2["total_price"] == round(2 * daily_price, 2)  # 2 * 39.50 = 79.0

    # --- 5) persistence check: bookings.json contains exactly these two rows for this car ---
    bookings_path = Path("data/bookings.json")
    assert bookings_path.exists(), "bookings.json should exist"
    store = json.loads(bookings_path.read_text(encoding="utf-8"))

    items = store.get("items", {})
    assert isinstance(items, dict) and len(items) >= 2

    mine = [doc for doc in items.values() if doc.get("car_id") == car_id]
    assert len(mine) == 2

    # verify the stored ranges match what we created
    ranges = {(doc["start_date"], doc["end_date"]) for doc in mine}
    assert (start1, end1) in ranges
    assert (start2, end2) in ranges

def test_create_booking_by_id_success(client):
    res = client.post("/api/bookings", json={
        "car_id": 1,
        "start_date": "2025-09-20",
        "end_date": "2025-09-22"
    })
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["car_id"] == 1
    assert data["start_date"] == "2025-09-20"
    assert data["end_date"] == "2025-09-22"
    assert data["days"] == 3
    assert data["total_price"] == 150.0

    txt = _read_bookings_json_text()
    assert '"car_id": 1' in txt
    assert '"start_date": "2025-09-20"' in txt
    assert '"end_date": "2025-09-22"' in txt
    assert '"days": 3' in txt
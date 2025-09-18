import logging
from datetime import date
from typing import Dict, Any, List

logger = logging.getLogger("app.service.booking")

def _validate_and_days(start: date, end: date) -> int:
    if end <= start:
        raise ValueError("end_date must be after start_date")
    return (end - start).days

def _overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return a_start < b_end and b_start < a_end

def _row_to_range(b: Dict[str, Any]) -> tuple[date, date]:
    bs = date.fromisoformat(str(b["start_date"]))
    be = date.fromisoformat(str(b["end_date"]))
    return bs, be

def ensure_available_and_create_booking(
    cars_repo, bookings_repo, car_id: int, start: date, end: date
) -> Dict[str, Any]:
    car = cars_repo.get(car_id)
    if not car or not car.get("active", True):
        logger.warning("booking_failed car_missing_or_inactive car_id=%s", car_id)
        raise ValueError("Car not found or inactive")

    days = _validate_and_days(start, end)

    for b in bookings_repo.list():
        if b["car_id"] != car_id:
            continue
        bs, be = _row_to_range(b)
        if _overlaps(start, end, bs, be):
            logger.info("booking_failed conflict car_id=%s start=%s end=%s", car_id, start.isoformat(), end.isoformat())
            raise ValueError("Car already booked for that period")

    doc = {
        "car_id": car_id,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "days": days,
    }
    created = bookings_repo.insert(doc)
    logger.info("booking_success id=%s car_id=%s start=%s end=%s days=%s",
                created["id"], car_id, start.isoformat(), end.isoformat(), days)
    return created

def list_available_cars_for_period(
    cars_repo, bookings_repo, start: date, end: date
) -> List[Dict[str, Any]]:
    _validate_and_days(start, end)

    booked: dict[int, list[tuple[date, date]]] = {}
    for b in bookings_repo.list():
        cid = b["car_id"]
        bs, be = _row_to_range(b)
        booked.setdefault(cid, []).append((bs, be))

    available: List[Dict[str, Any]] = []
    for c in cars_repo.list():
        if not c.get("active", True):
            continue
        cid = c["id"]
        ranges = booked.get(cid, [])
        if any(_overlaps(start, end, bs, be) for (bs, be) in ranges):
            continue
        available.append(c)

    logger.info("available_cars start=%s end=%s result=%d", start.isoformat(), end.isoformat(), len(available))
    return available

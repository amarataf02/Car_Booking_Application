from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
import logging

from app.models.schemas import Booking, BookingCreate
from app.json_handler.json_store import JSONStore
from app.json_handler.db_handler import GenericRepo

router = APIRouter(tags=["Bookings"])
logger = logging.getLogger("app.booking_endpoint")

def cars_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/cars.json")))

def bookings_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/bookings.json")))

@router.get("/bookings", response_model=List[Booking])
def list_bookings():
    rows = bookings_repo().list()
    logger.info("list_bookings count=%d")
    return rows

@router.get("/bookings/by-car/{car_id}", response_model=List[Booking])
def bookings_by_car(car_id: int):
    rows = [b for b in bookings_repo().list() if b["car_id"] == car_id]
    logger.info("bookings_by_car car_id=%s count=%d", car_id, len(rows))
    return rows

@router.post("/bookings", response_model=Booking, status_code=201)
def create_booking(body: BookingCreate):
    iso = body.date.isoformat()

    car = cars_repo().get(body.car_id)
    if not car or not car.get("active", True):
        logger.warning("booking_failed car_missing_or_inactive car_id=%s date=%s", body.car_id, iso)
        raise HTTPException(status_code=400, detail="Car not found or inactive")

    for b in bookings_repo().list():
        if b["car_id"] == body.car_id and str(b["date"]) == iso:
            logger.info("booking_failed conflict car_id=%s date=%s", body.car_id, iso)
            raise HTTPException(status_code=400, detail="Car already booked for that date")

    doc = {"car_id": body.car_id, "date": iso, "customer_name": body.customer_name}
    created = bookings_repo().insert(doc)
    logger.info("booking_success id=%s car_id=%s date=%s", created["id"], body.car_id, iso)
    return created

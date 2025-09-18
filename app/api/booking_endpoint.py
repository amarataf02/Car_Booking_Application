from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
import logging

from app.models.schemas import Booking, BookingCreate
from app.json_handler.json_store import JSONStore
from app.json_handler.db_handler import GenericRepo
from app.service.booking_service import ensure_available_and_create_booking

router = APIRouter(tags=["Bookings"])
logger = logging.getLogger("app.booking_endpoint")

def cars_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/cars.json")))

def bookings_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/bookings.json")))

@router.get("/bookings", response_model=List[Booking])
def list_bookings():
    rows = bookings_repo().list()
    logger.info("list_bookings count=%d", len(rows))
    return rows

@router.get("/bookings/by-car/{car_id}", response_model=List[Booking])
def bookings_by_car(car_id: int):
    rows = [b for b in bookings_repo().list() if b["car_id"] == car_id]
    logger.info("bookings_by_car car_id=%s count=%d", car_id, len(rows))
    return rows

@router.post("/bookings", response_model=Booking, status_code=201)
def create_booking(body: BookingCreate):
    try:
        created = ensure_available_and_create_booking(
            cars_repo(), bookings_repo(), body.car_id, body.start_date, body.end_date
        )
        return created
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

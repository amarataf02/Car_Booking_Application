from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List

from app.models.schemas import Booking, BookingCreate
from app.json_handler.json_store import JSONStore
from app.json_handler.db_handler import GenericRepo

router = APIRouter()

def cars_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/cars.json")))

def bookings_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/bookings.json")))

@router.get("/bookings", response_model=List[Booking])
def list_bookings():
    return bookings_repo().list()

@router.get("/bookings/by-car/{car_id}", response_model=List[Booking])
def bookings_by_car(car_id: int):
    rows = bookings_repo().list()
    return [b for b in rows if b["car_id"] == car_id]

@router.post("/bookings", response_model=Booking, status_code=201)
def create_booking(body: BookingCreate):
    car = cars_repo().get(body.car_id)
    if not car or not car.get("active", True):
        raise HTTPException(status_code=400, detail="Car not found or inactive")

    iso = body.date.isoformat()
    for b in bookings_repo().list():
        if b["car_id"] == body.car_id and str(b["date"]) == iso:
            raise HTTPException(status_code=400, detail="Car already booked for that date")

    doc = {"car_id": body.car_id, "date": iso, "customer_name": body.customer_name}
    return bookings_repo().insert(doc)

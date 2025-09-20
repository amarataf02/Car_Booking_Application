from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
import logging

from app.models.schemas import Booking, BookingCreate, BookingCreateBySeats, BookingWithPrice
from app.json_handler.json_store import JSONStore
from app.json_handler.db_handler import GenericRepo
from app.service.booking_service import ensure_available_and_create_booking, book_by_seats

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

@router.post("/bookings", response_model=BookingWithPrice, status_code=201)
def create_booking(body: BookingCreate):
    try:
        created = ensure_available_and_create_booking(
            cars_repo(), bookings_repo(), body.car_id, body.start_date, body.end_date
        )
        return created
    except ValueError as ex:
        detail = ex.args[0] if isinstance(ex.args[0], dict) else {"message": str(ex)}
        raise HTTPException(status_code=400, detail=detail)

@router.post("/bookings/by-seats", response_model=BookingWithPrice, status_code=201)
def create_booking_by_seats(body: BookingCreateBySeats):
    try:
        created = book_by_seats(
            cars_repo(), bookings_repo(),
            seats=body.seats,
            start=body.start_date,
            end=body.end_date
        )
        logger.info(
            "booking_by_seats_success id=%s seats=%s start=%s end=%s",
            created["id"], body.seats, body.start_date.isoformat(), body.end_date.isoformat()
        )
        return created
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.delete("/bookings/{booking_id}", status_code=204, summary="Cancel a booking")
def delete_booking(booking_id: int):
    repo = bookings_repo()
    booking = repo.get(booking_id)
    if not booking:
        logger.warning("delete_booking_failed id=%s not_found", booking_id)
        raise HTTPException(status_code=404, detail="Booking not found")

    repo.delete(booking_id)
    logger.info(
        "delete_booking_success id=%s car_id=%s start=%s end=%s",
        booking_id, booking["car_id"], booking["start_date"], booking["end_date"]
    )
    return {"detail": f"Booking {booking_id} cancelled successfully"}
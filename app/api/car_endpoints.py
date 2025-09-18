import logging
from datetime import date
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List

from app.models.schemas import Car, CarCreate
from app.json_handler.json_store import JSONStore
from app.json_handler.db_handler import GenericRepo
from app.service.booking_service import list_available_cars_for_period

router = APIRouter(tags=["Cars"])
logger = logging.getLogger("app.cars")

def cars_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/cars.json")))

def bookings_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/bookings.json")))

@router.get("/cars/available", summary="List available cars for a period")
def cars_available(start: date, end: date):
    try:
        cars = list_available_cars_for_period(cars_repo(), bookings_repo(), start, end)
        return {"start": start, "end": end, "cars": cars}
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get("/cars", response_model=List[Car])
def list_cars():
    rows = cars_repo().list()
    logger.info("list_cars count=%d", len(rows))
    return rows

@router.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int):
    car = cars_repo().get(car_id)
    if not car:
        logger.info("get_car not_found id=%s", car_id)
        raise HTTPException(status_code=404, detail="Car not found")
    logger.info("get_car ok id=%s", car_id)
    return car

@router.post("/cars", response_model=Car, status_code=201)
def create_car(body: CarCreate):
    created = cars_repo().insert(body.model_dump())
    logger.info("create_car ok id=%s make=%s model=%s", created["id"], created.get("make"), created.get("model"))
    return created
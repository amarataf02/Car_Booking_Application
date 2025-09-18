from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List

from app.models.schemas import Car, CarCreate
from app.json_handler.json_store import JSONStore
from app.json_handler.db_handler import GenericRepo

router = APIRouter()

def cars_repo() -> GenericRepo:
    return GenericRepo(JSONStore(Path("data/cars.json")))

@router.get("/cars", response_model=List[Car])
def list_cars():
    return cars_repo().list()

@router.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int):
    car = cars_repo().get(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@router.post("/cars", response_model=Car, status_code=201)
def create_car(body: CarCreate):
    doc = body.model_dump()
    return cars_repo().insert(doc)
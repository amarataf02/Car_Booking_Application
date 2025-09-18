import json
import logging
from pathlib import Path
from fastapi import APIRouter

from app.json_handler.json_store import JSONStore
from app.json_handler.db_handler import GenericRepo

router = APIRouter()
logger = logging.getLogger("app.seed")

DATA_CARS = Path("data/cars.json")

def cars_repo() -> GenericRepo:
    return GenericRepo(JSONStore(DATA_CARS))

@router.post("/seed/cars")
def seed_cars(reset: bool = False):
    DATA_CARS.parent.mkdir(parents=True, exist_ok=True)

    if reset:
        DATA_CARS.write_text('{ "_meta": { "seq": 0 }, "items": {} }', encoding="utf-8")
        logger.info("seed_cars reset=true: cars.json cleared")

    repo = cars_repo()
    existing = repo.list()
    if existing and not reset:
        logger.info("seed_cars skipped: already populated count=%d", len(existing))
        return {"inserted": 0, "skipped": True, "existing_count": len(existing)}

    seed = [
        {"make": "Toyota", "model": "Corolla", "seats": 5, "daily_price": 45.0, "active": True},
        {"make": "Tesla",  "model": "Model 3", "seats": 5, "daily_price": 80.0, "active": True},
        {"make": "VW",     "model": "Golf",    "seats": 5, "daily_price": 50.0, "active": True},
    ]
    created = [repo.insert(car) for car in seed]
    logger.info("seed_cars done: reset=%s inserted=%d", reset, len(created))
    return {"inserted": len(created), "cars": created}
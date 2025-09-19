import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

def _init_empty_store(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"_meta": {"seq": 0}, "items": {}}), encoding="utf-8")

@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    # Each test run gets its own CWD and its own data/ folder
    monkeypatch.chdir(tmp_path)

    data_dir = Path("data")
    cars_path = data_dir / "cars.json"
    bookings_path = data_dir / "bookings.json"
    _init_empty_store(cars_path)
    _init_empty_store(bookings_path)

    # Import AFTER CWD is set so your relative Path("data/...") works
    from app.json_handler.json_store import JSONStore
    from app.json_handler.db_handler import GenericRepo
    from app.main import app

    # Seed cars (deterministic IDs: 1,2,3)
    cars_repo = GenericRepo(JSONStore(cars_path))
    cars_repo.insert({"make": "Toyota", "model": "Corolla", "seats": 5, "daily_price": 50.0})
    cars_repo.insert({"make": "Tesla",  "model": "Model 3","seats": 5, "daily_price": 70.0})
    cars_repo.insert({"make": "VW",     "model": "Sharan", "seats": 7, "daily_price": 90.0})

    return TestClient(app)

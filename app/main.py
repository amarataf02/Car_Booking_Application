from fastapi import FastAPI
from app.core.logger import init_logging
from app.api.logs_endpoints import router as logs_router
from app.api.car_endpoints import router as cars_router
from app.api.booking_endpoint import router as bookings_router
from app.api.seed import router as seed_router

tags_metadata = [
    {"name": "Cars", "description": "Operations to list, read, and create cars."},
    {"name": "Bookings", "description": "Create bookings and view them."},
    {"name": "Admin Pannel", "description": "Admin endpoints for seeding db and logging"},
]

init_logging()

app = FastAPI(
    title="Car Rental API (JSON-backed)",
    version="0.1.0",
    description="Simple demo API using JSON files for storage.",
    openapi_tags=tags_metadata,
)

app = FastAPI(title="Car Rental API (JSON-backed)")
app.include_router(cars_router, prefix="/api")
app.include_router(bookings_router, prefix="/api")
app.include_router(logs_router, prefix="/api")
app.include_router(seed_router, prefix="/api") 
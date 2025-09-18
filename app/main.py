from fastapi import FastAPI
from app.core.logger import init_logging
from app.api.logs_endpoints import router as logs_router
from app.api.car_endpoints import router as cars_router
from app.api.booking_endpoint import router as bookings_router
from app.api.seed import router as seed_router

init_logging()

app = FastAPI(title="Car Rental API (JSON-backed)")
app.include_router(cars_router, prefix="/api")
app.include_router(bookings_router, prefix="/api")
app.include_router(logs_router, prefix="/api")
app.include_router(seed_router, prefix="/api") 
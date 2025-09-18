from fastapi import FastAPI
from app.api.car_endpoints import router as cars_router
from app.api.booking_endpoint import router as bookings_router

app = FastAPI(title="Car Rental API (JSON-backed)")
app.include_router(cars_router, prefix="/api")
app.include_router(bookings_router, prefix="/api")
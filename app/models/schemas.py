from pydantic import BaseModel
from datetime import date

class Car(BaseModel):
    id: int
    make: str
    model: str
    seats: int
    daily_price: float
    active: bool = True

class CarCreate(BaseModel):
    make: str
    model: str
    seats: int
    daily_price: float
    active: bool = True

class Booking(BaseModel):
    id: int
    car_id: int
    start_date: date
    end_date: date
    days: int

class BookingCreate(BaseModel):
    car_id: int
    start_date: date
    end_date: date

class BookingCreateBySeats(BaseModel):
    seats: int
    start_date: date
    end_date: date

class BookingWithPrice(Booking):
    total_price: float
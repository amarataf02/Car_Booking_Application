from pydantic import BaseModel
from datetime import date

class Car(BaseModel):
    id: int
    make: str
    model: str
    seats: int
    daily_price: float
    active: bool = True

class Booking(BaseModel):
    id: int
    car_id: int
    date: date
    customer_name: str

class BookingCreate(BaseModel):
    car_id: int
    date: date
    customer_name: str

class CarCreate(BaseModel):
    make: str
    model: str
    seats: int
    daily_price: float
    active: bool = True
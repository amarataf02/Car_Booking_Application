Car Rental API (JSON-backed)

A tiny FastAPI project that simulates a car-rental backend using JSON files as storage. It focuses on the two core flows:

Check availability of cars for a date range

Create a booking for a date range (by car id or by number of seats)

It’s intentionally simple but structured like a real app: routing → service layer → repository → storage. That makes it easy to swap JSON for a real database later.

Architecture & Design Choices

Storage (per spec): uses JSON files instead of a database:

data/cars.json (“cars table”)

data/bookings.json (“bookings table”)

Repository pattern: to mimic DB/ORM access, there’s a small abstraction over JSON files:

repo.list(), repo.get(id), repo.insert(doc), repo.delete(id)

This keeps API/service code database-agnostic and swappable with a real DB later.

JSONStore (file wrapper):

Applies file locking during writes and performs atomic rewrites to avoid corruption.

Simulates a “single-writer” model so two writers don’t edit at the same time.

Why this is scalable later: the API and service layers already talk to a “DB-like” interface (the repo). Replacing GenericRepo(JSONStore(...)) with a real database repo is a drop-in change.

Dates & range logic:

Inclusive ranges: [start_date, end_date]

days = (end_date - start_date).days + 1 (so start == end means 1 day)

Overlap rule (inclusive): two bookings overlap if
a_start <= b_end AND b_start <= a_end

Pricing: booking responses include total_price = days * daily_price.

Endpoints

Base path: /api

Focus endpoints

GET /cars/available — list available cars for a date range

POST /bookings — create a booking by car id

POST /bookings/by-seats — create a booking by seat count (first available)

Method	Path	What it does	Body (JSON) example
GET	/cars	List all cars.	—
GET	/cars/{car_id}	Get a single car by id.	—
POST	/cars	Create a new car.	{"make":"Toyota","model":"Corolla","seats":5,"daily_price":50.0}
GET	/cars/available?start=YYYY-MM-DD&end=YYYY-MM-DD	Availability: cars not overlapping any booking within the inclusive [start,end] range.	—
GET	/bookings	List all bookings.	—
GET	/bookings/by-car/{car_id}	List bookings for a car.	—
POST	/bookings	Create booking by car id. Returns days and total_price.	{"car_id":1,"start_date":"2025-09-20","end_date":"2025-09-22"}
POST	/bookings/by-seats	Create booking by seats (first available car with that seat count). Returns days and total_price.	{"seats":5,"start_date":"2025-09-20","end_date":"2025-09-22"}
GET	/logs?n=200	Tail the last N log lines (plain text).	—
POST	`/seed/cars?reset=true	false`	Seed some demo cars. reset=true rewrites cars.json.

Responses (booking creation):

{
  "id": 7,
  "car_id": 2,
  "start_date": "2025-09-20",
  "end_date": "2025-09-22",
  "days": 3,
  "total_price": 210.0
}

Folders (what’s inside)

app/api/ — FastAPI routers (cars, bookings, logs, seed)

app/core/ — logging setup (stdout + file)

app/json_handler/ — JSONStore (file IO + locking) and GenericRepo (list/get/insert/delete)

app/models/ — Pydantic schemas (Car, Booking, etc.)

app/service/ — business rules (availability, conflict checks, pricing)

app/main.py — app factory & OpenAPI tag metadata

data/ — JSON files (created at runtime)

logs/ — log file (created at runtime)

tests/ — pytest integration tests

Testing (Quality Assurance)

pytest + FastAPI TestClient

Tests use a temporary data/ per test run (no real files touched).

They call real endpoints (HTTP) and validate:

booking creation by id & by seats

inclusive edge conflicts

total price calculations

availability results

persistence by reading data/bookings.json

Run tests (Docker Compose):

docker compose exec api pytest -vv


You can also test everything interactively at /docs (Swagger UI).

Setup & Run
Docker Compose (recommended)

Build & start:

docker compose up --build


Open docs:

http://localhost:8000/docs


(Optional) Seed demo cars:

curl -X POST "http://localhost:8000/api/seed/cars?reset=true"


Tail logs (last 200 lines):

curl "http://localhost:8000/api/logs?n=200"

Local (without Docker)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Logging

Initialized once at startup; logs go to stdout and a file (e.g., logs/app.log).

Developer helper endpoint:

GET /api/logs?n=200 → returns the last N lines (plain text), useful during development.

How Date Ranges Are Computed (Simple & Predictable)

Bookings use inclusive ranges: [start_date, end_date]

Days are computed as:

days = (end_date - start_date).days + 1


Overlaps are checked with:

overlaps = (a_start <= b_end) and (b_start <= a_end)


This guarantees:

start == end → 1-day booking

A booking starting on another booking’s end day conflicts (not allowed)

Potential Improvements

Replace JSON with a real database (e.g., Postgres/SQLite) + migrations

Auth & rate limiting

Time zones and pickup/return times (currently date-only)

Pagination & filters for listings

Better error messages & suggestions (alternative cars/dates)

Availability caching for large datasets

Idempotency keys for booking creation (safe retries)

Multi-process distributed locks (or just use a DB for concurrency)

License

MIT (or your preferred license)

Tip: Everything is browsable and testable at /docs. The structure is deliberately close to a “real” service so swapping the JSON repo for a proper database later is straightforward.
# Car Rental API

A tiny FastAPI project that simulates a car-rental backend using JSON files as storage.  
It focuses on two core flows:

- **Check availability of cars** for a date range  
- **Create a booking** for a date range (by car id or by number of seats)

The app is intentionally simple but structured like a real service:  
`routing → service layer → repository → storage`.  
This makes it easy to replace JSON with a real database later.

## Suggestion system

The app suggests cars with similar features when a car is already booked for the desired dates.

---

## Design Choices

### Storage
(Per the exercise spec): plain JSON files instead of a DB

- `data/cars.json` → “cars table”  
- `data/bookings.json` → “bookings table”  

### JSON as a mini database
To keep the app scalable and DB-agnostic, all reads/writes go through a tiny repository layer:
- JSONStore: low-level file I/O + file locking; reads the JSON, applies a change, and rewrites atomically (write to temp file, then replace). This prevents partial writes and concurrent corruption.
- GenericRepo: simple CRUD-like API on top of the store:
  - `list()` → return all rows (list of dicts)
  - `get(id)` → return one row or None
  - `insert(doc)` → assign next ID (_meta.seq + 1), persist, return created row
  - `delete(id)` → remove row if present

**Why this scales later:**  
the API and services only know about list/get/insert/delete, not how data is stored. Swapping `GenericRepo(JSONStore(...))` for a real repository (e.g., SQLAlchemy/ORM) is a localized change with minimal impact on routes/services.

### Integration of new tables

Each `GenericRepo` instance is tied to a single `JSONStore`, which in turn maps to one `JSON file`. You can think of this like opening a database connection to a specific table.
- For example, `GenericRepo(JSONStore("data/cars.json"))` is the repository for the cars table.
- Similarly, `GenericRepo(JSONStore("data/bookings.json"))` handles the bookings table.
All operations `(list, get, insert, delete)` on that repo are automatically routed to the correct file via the `JSONStore`, which ensures atomic reads and writes with file locking.

**This design makes adding a new table straightforward:**
- Create a new JSON file (e.g., data/customers.json).
- Initialize a new repo:
  `customers_repo = GenericRepo(JSONStore("data/customers.json"))`
- Use it in exactly the same way as other repos:
  `customers_repo.insert({"name": "Alice"})`

**Because each repo is isolated to its file, this pattern is scalable:**
- Adding a new "table" = creating a new JSON file + new GenericRepo binding.
- From the service or API perspective, this behaves just like a real DB session:
  - Instead of `db.add(customer)` → you call `customers_repo.insert(customer)`
  - Instead of `db.query(Customer)` → you call `customers_repo.list()`

This keeps the code clean, consistent, and swappable with a real ORM (like SQLAlchemy) in the future.

### Booking options & pricing

- **Create booking by car ID:** book a specific car for a date range.
- **Create booking by seats:** pick the first available car with the requested seat count for a date range.
- **Price:** responses include `total_price = days * daily_price` (rounded to 2 decimals).
The computed days is also stored with the booking for clarity.

### Dates & ranges

- Inclusive ranges: `[start_date, end_date]`
- days = (end_date - start_date).days + 1 (so start == end is 1 day)  
- Overlap check (inclusive): two bookings overlap if `a_start <= b_end AND b_start <= a_end`

### Guarantees
- start == end → 1 day  
- A booking starting on another booking’s end day conflicts (not allowed)

---

## Architecture

### Endpoints (brief)

**Base path:** /api

### Cars
- GET /cars  
- GET /cars/{car_id}  
- POST /cars  
- GET /cars/available?start=YYYY-MM-DD&end=YYYY-MM-DD

### Bookings
- GET /bookings  
- GET /bookings/by-car/{car_id}  
- POST /bookings  
- POST /bookings/by-seats
- DELETE /booking/{booking_id}

### Utilities
- GET /logs?n=200  
- POST /seed/cars?reset=true|false

Explore & try everything at:

- /docs (Swagger UI)  
- /redoc

---

## Folders (what’s inside)

- `app/api/` — FastAPI routers (cars, bookings, logs, seed)  
- `app/core/` — logging setup (stdout + file)  
- `app/json_handler/` — JSONStore (file IO + locking) & Database handler (CRUD-ish)  
- `app/models/` — Pydantic schemas (Car, Booking, etc.)  
- `app/service/` — business rules (availability, conflicts, pricing)  
- `app/main.py` — app wiring & OpenAPI tags  
- `data/` — JSON files (created at runtime)  
- `tests/` — pytest integration tests  

---

## Testing (Quality Assurance)

- Frameworks: pytest + FastAPI TestClient  
- **Unit testing for booking endpoints**
- **Integration testing of full circle logic:**
  - `car creation →  car checking → availability checking → booking of car -> check booking -> check persistance`
- Tests run against a temporary data/ per test (no real files touched)  
- They call real endpoints and validate:
  - booking creation (by id & by seats)  
  - inclusive edge conflicts  
  - total price math  
  - availability behavior  
  - persistence by reading data/bookings.json  

Run tests (execute in different terminal if not running docker container in the background):
```bash
docker compose exec api pytest -vv
```

---

## Setup & Run

### Clone the repository

```bash
git clone https://github.com/amarataf02/Car_Booking_Application.git
cd Car_Booking_Application
```

### Docker Compose (recommended)

```bash
docker compose up --build
```

**Open the docs:**

- Swagger UI -> http://localhost:8000/docs
- ReDoc -> http://localhost:8000/redoc

Seed demo cars from:  
`/api/seed/cars?reset=true`

Tail logs (last 200 lines) from:  
`/api/logs?n=200`

---

## Logging

- Initialized on startup  
- Logs to stdout and a file under logs/ (e.g., logs/app.log)  

Dev helper endpoint:  
`GET /api/logs?n=200 → returns the last N lines (plain text)`

---

## Potential Improvements

- Replace JSON with a real database (Postgres/SQLite) and migrations with Alembic
- Authentication & rate limiting  
- Time zones and pickup/return times (currently date-only)  
- Pagination & filters for listings  
- Better conflict feedback (suggest alternative cars/dates)  
- Availability caching for large datasets  
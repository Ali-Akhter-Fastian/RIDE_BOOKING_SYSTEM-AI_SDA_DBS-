# RIDE_BOOKING_SYSTEM-AI_SDA_DBS-

FastAPI authentication backend for the ride booking system.

## Structure

The project keeps only app bootstrap files in `app/`:

- `app/__init__.py`
- `app/main.py`
- `app/config.py`
- `app/dependencies.py`

Feature and domain modules are top-level packages:

- `api/`
- `core/`
- `db/`
- `exception/`
- `models/`
- `repositories/`
- `schemas/`
- `services/`
- `utils/`
- `tests/`

## Setup

1. Copy `.env.example` to `.env` and set `DB_URL` and `JWT_SECRET`.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the PostgreSQL migration in [migrations/001_users.sql](migrations/001_users.sql).
4. Start the API with `uvicorn app.main:app --reload`.

## Auth Routes

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
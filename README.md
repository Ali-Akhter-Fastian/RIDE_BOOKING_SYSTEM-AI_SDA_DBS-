# Ride Booking API

A FastAPI-based rides service for booking, querying, and managing ride reservations.

## Overview

This repository contains the backend API for a ride booking platform. It uses:

- FastAPI for HTTP routing and request handling
- asyncpg for PostgreSQL database access
- Alembic for database migrations
- JWT for authentication support
- Pydantic for request/response validation

## Requirements

- Python 3.11+ recommended
- PostgreSQL database
- `pip` package manager

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd ride_api
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure values:

   ```bash
   copy .env.example .env
   ```

5. Edit `.env` and set the following required values:

   - `DB_URL` or `DATABASE_URL`
   - `JWT_SECRET`
   - Optional values: `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_MINUTES`, `DB_POOL_MIN_SIZE`, `DB_POOL_MAX_SIZE`

## Running the API

Start the server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is mounted under the `/api` prefix.

## Testing

Run unit tests with pytest:

```bash
pytest
```

## Database Migrations

Alembic is configured in `alembic.ini` and uses `.env` variables for the database URL.

To apply migrations:

```bash
alembic upgrade head
```

## Project Structure

- `app/` — application configuration and startup
- `api/` — API router and endpoint modules
- `db/` — database connection and query handling
- `models/` — domain models
- `repositories/` — persistence layer for rides
- `schemas/` — Pydantic request/response schemas
- `services/` — business logic for ride operations
- `tests/` — unit tests
- `migrations/` — Alembic migration scripts

## Notes

- The `.env.example` file contains the expected environment variables.
- Do not commit `.env` to version control.
- Ensure PostgreSQL is running and accessible before starting the API.

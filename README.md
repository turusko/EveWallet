# EVE Online Project Profit Tracker (Phase 1 Backend)

FastAPI backend MVP for linking multiple EVE characters via SSO, syncing wallet transactions and market orders, assigning imported records to project buckets, and calculating simple bucket P&L summaries.

## Tech stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- httpx
- Pydantic

## Prerequisites

- Python 3.12+
- PostgreSQL 16+ (or Docker)
- `pip`

## Environment variables

Copy `.env.example` to `.env` and set values:

```bash
cp .env.example .env
```

Required variables:

- `APP_ENV`
- `APP_HOST`
- `APP_PORT`
- `DATABASE_URL`
- `SECRET_KEY`
- `EVE_CLIENT_ID`
- `EVE_CLIENT_SECRET`
- `EVE_REDIRECT_URI`
- `EVE_SSO_AUTHORIZE_URL`
- `EVE_SSO_TOKEN_URL`
- `EVE_ESI_BASE_URL`

## Create DB

```bash
createdb eve_tracker
```

Or use Docker compose:

```bash
docker compose up -d db
```

## Install dependencies

```bash
pip install -e .[dev]
```

## Run migrations

```bash
alembic upgrade head
```

## Start dev server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## EVE SSO app configuration

1. Create third-party app in EVE Developers portal.
2. Set callback URL to `EVE_REDIRECT_URI` (default: `http://localhost:8000/auth/callback`).
3. Copy client ID + secret into `.env`.

### Required scopes

- `esi-wallet.read_character_wallet.v1`
- `esi-markets.read_character_orders.v1`

## API flow

1. `GET /auth/login`
2. Complete EVE SSO in browser
3. `GET /auth/callback?code=...`
4. Repeat steps 1-3 to link additional characters
5. `POST /wallet/sync/{character_id}`
6. `POST /orders/sync/{character_id}`
7. Create bucket, assign records, fetch reports

## Example curl commands

```bash
curl http://localhost:8000/health
curl http://localhost:8000/auth/login
curl -X POST http://localhost:8000/buckets \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: <user_uuid>' \
  -d '{"name":"Jita Flip","description":"April market run"}'
curl -X GET "http://localhost:8000/reports/buckets/<bucket_id>/summary" -H 'X-User-Id: <user_uuid>'
```

## Docker compose (app + postgres)

```bash
docker compose up --build
```

## Test

```bash
pytest
```

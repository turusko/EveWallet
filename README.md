# EVE Online Project Profit Tracker (Phase 2 Backend)

FastAPI backend for linking EVE characters, syncing wallet transactions/journal/orders (active + historical), assigning records into project buckets, running automatic assignment rules, scheduling sync jobs, and exporting bucket reports.

## Tech stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- httpx
- Redis + RQ
- Pydantic

## Environment variables

Copy `.env.example` to `.env` and set values.

Required + new Phase 2 values:

- `DATABASE_URL`
- `SECRET_KEY`
- `EVE_CLIENT_ID`
- `EVE_CLIENT_SECRET`
- `EVE_REDIRECT_URI`
- `EVE_ESI_BASE_URL`
- `REDIS_URL=redis://localhost:6379/0`
- `SYNC_USE_BACKGROUND_WORKER=true`
- `SYNC_INTERVAL_MINUTES=15`

## Install and run

```bash
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Redis and worker startup

```bash
docker compose up -d db
redis-server
rq worker
```

Worker task path used by RQ:

```bash
app.worker.run_sync_job
```

## Scheduled sync behavior

- `POST /sync/character/{character_id}` enqueues (or runs inline when background worker is disabled) a character sync job.
- `POST /sync/all` syncs every linked character for the current user.
- `GET /sync/jobs` and `GET /sync/jobs/{job_id}` expose job statuses and metrics.
- Development setups can trigger recurring syncs every `SYNC_INTERVAL_MINUTES`.

## Rule creation and rerun

Rules are evaluated in ascending `priority`; matching uses AND semantics on `conditions_json`.

Create rule example:

```bash
curl -X POST http://localhost:8000/rules \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: <user_uuid>' \
  -d '{
    "bucket_fk": "<bucket_uuid>",
    "name": "Tax and Fees",
    "priority": 10,
    "stop_processing": true,
    "conditions_json": {
      "ref_types": ["transaction_tax", "brokers_fee"]
    }
  }'
```

Rerun rules example:

```bash
curl -X POST http://localhost:8000/rules/run \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: <user_uuid>' \
  -d '{"only_unassigned": true, "force_reassign": false}'
```

## Manual sync endpoints

- `POST /wallet/sync/{character_id}`
- `POST /wallet-journal/sync/{character_id}`
- `POST /orders/sync/{character_id}?include_history=true`

## Reporting and CSV export

- `GET /reports/buckets/{bucket_id}/summary`
- `GET /reports/buckets/{bucket_id}/export.csv`
- `GET /reports/buckets/export.csv`

Phase 2 realised P&L remains a **cashflow-based estimate** (not FIFO inventory lot accounting).

## Test

```bash
pytest
```

# EVE Online Project Profit Tracker (Phase 3)

Phase 3 extends cashflow tracking into inventory-aware accounting with FIFO lots, assets, industry jobs, contracts, and a minimal React UI.

## Stack
- Backend: FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, Redis/RQ, httpx, Pydantic.
- Frontend: React + Vite + TypeScript + Tailwind, TanStack Query, TanStack Table-ready pages.

## Backend setup
```bash
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend setup
```bash
cd frontend
npm install
npm run dev
```

## Redis worker startup
```bash
redis-server
rq worker
```

## Docker compose
```bash
docker compose up --build
```
Runs backend, frontend, postgres, and redis.

## EVE SSO setup
Use EVE SSO OAuth 2.0 with your app credentials and callback URL. Configure:
- `EVE_CLIENT_ID`
- `EVE_CLIENT_SECRET`
- `EVE_REDIRECT_URI`
- `EVE_SSO_AUTHORIZE_URL`
- `EVE_SSO_TOKEN_URL`
- `EVE_ESI_BASE_URL`

### Recommended scopes for Phase 3
- Wallet/transactions/journal scopes from earlier phases.
- Assets scope for character assets sync.
- Industry jobs scope for character industry sync.
- Contracts scope for character contracts sync.
- Structure read scope for resolving Upwell structure names when accessible.

## Environment variables
Backend:
```env
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/eve_tracker
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change_me
EVE_CLIENT_ID=...
EVE_CLIENT_SECRET=...
EVE_REDIRECT_URI=http://localhost:8000/auth/callback
EVE_SSO_AUTHORIZE_URL=https://login.eveonline.com/v2/oauth/authorize
EVE_SSO_TOKEN_URL=https://login.eveonline.com/v2/oauth/token
EVE_ESI_BASE_URL=https://esi.evetech.net/latest
FRONTEND_ORIGIN=http://localhost:5173
```

Frontend:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Structure resolution
`StructureService` resolves and caches location names in `resolved_locations`. If name resolution is unavailable due to access restrictions, responses keep a best-effort unresolved marker (`unresolved:<id>`), rather than failing sync.

## FIFO accounting behavior
- New inventory lots are created for acquisitions (wallet buys, contract/industry integrations).
- Sales/material consumption consume oldest open lots first (FIFO).
- Realised COGS is based on consumed lots.
- Remaining lot quantities produce inventory-on-hand valuation.

## Known limitations
- No corp wallet/corp assets yet.
- No weighted-average costing yet.
- Unmatched sales can occur if prior inventory is missing.
- Some structure names remain unresolved if authenticated access is unavailable.

## Tests
```bash
pytest
```

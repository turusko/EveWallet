import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import assets, auth, buckets, characters, contracts, industry, inventory, orders, reports, rules, sync, wallet, wallet_journal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="EVE Project Profit Tracker")
FRONTEND_DIST_DIR = Path("/app/frontend_dist")
HAS_FRONTEND = FRONTEND_DIST_DIR.exists()

app.include_router(auth.router)
app.include_router(characters.router)
app.include_router(wallet.router)
app.include_router(orders.router)
app.include_router(wallet_journal.router)
app.include_router(buckets.router)
app.include_router(rules.router)
app.include_router(sync.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    if HAS_FRONTEND:
        return RedirectResponse(url="/tools", status_code=307)
    return RedirectResponse(url="/docs", status_code=307)


@app.get("/home")
def home() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@app.get("/swagger")
def swagger_alias() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


app.include_router(assets.router)
app.include_router(inventory.router)
app.include_router(industry.router)
app.include_router(contracts.router)

if HAS_FRONTEND:
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")

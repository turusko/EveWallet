import logging

from fastapi import FastAPI

from app.api.routes import auth, buckets, characters, orders, reports, rules, sync, wallet, wallet_journal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="EVE Project Profit Tracker")

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

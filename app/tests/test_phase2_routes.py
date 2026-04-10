from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.db.session import get_db
from app.main import app


class DummyUser:
    id = "00000000-0000-0000-0000-000000000001"


class DummyDB:
    def get(self, model, key):
        return type("Obj", (), {"id": key, "user_id": DummyUser.id})()


app.dependency_overrides[get_current_user] = lambda: DummyUser()
app.dependency_overrides[get_db] = lambda: DummyDB()
client = TestClient(app)


def test_sync_wallet_journal_endpoint(monkeypatch):
    from app.api.routes import wallet_journal

    class Svc:
        def __init__(self, db):
            pass

        async def sync(self, character):
            return 3

    monkeypatch.setattr(wallet_journal, "WalletJournalService", Svc)
    r = client.post("/wallet-journal/sync/abc")
    assert r.status_code == 200
    assert r.json()["inserted_or_updated"] == 3


def test_rule_crud_and_run(monkeypatch):
    from app.api.routes import rules

    class Svc:
        def __init__(self, db):
            pass

        def create(self, user_id, payload):
            return type("R", (), {"id": "1", "user_id": user_id, **payload.model_dump(), "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"})()

        def list(self, user_id):
            return []

        def get(self, user_id, rule_id):
            return None

        def update(self, user_id, rule_id, payload):
            raise ValueError("Rule not found")

        def delete(self, user_id, rule_id):
            return None

        def run(self, user_id, payload):
            return 4

    monkeypatch.setattr(rules, "AssignmentRuleService", Svc)
    run = client.post("/rules/run", json={"only_unassigned": True})
    assert run.status_code == 200
    assert run.json()["assignments_created"] == 4


def test_sync_all_characters_endpoint(monkeypatch):
    from app.api.routes import sync

    class Svc:
        def __init__(self, db):
            pass

        async def sync_all(self, user_id):
            return type("J", (), {"id": "1", "user_id": user_id, "job_type": "all", "status": "queued", "started_at": None, "finished_at": None, "details_json": {}})()

    monkeypatch.setattr(sync, "SyncSchedulerService", Svc)
    r = client.post("/sync/all")
    assert r.status_code == 200
    assert r.json()["status"] == "queued"


def test_csv_export_endpoint(monkeypatch):
    from app.api.routes import reports

    class BSvc:
        def __init__(self, db):
            pass

        def get(self, user_id, bucket_id):
            return type("B", (), {"id": bucket_id})()

    class RSvc:
        def __init__(self, db):
            pass

        def export_bucket_csv(self, bucket_id):
            return "a,b\n1,2\n"

        def export_all_buckets_csv(self, user_id):
            return "h\n"

    monkeypatch.setattr(reports, "BucketService", BSvc)
    monkeypatch.setattr(reports, "ReportService", RSvc)
    r = client.get("/reports/buckets/abc/export.csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]

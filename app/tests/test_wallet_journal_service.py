from datetime import datetime, UTC

from app.services.wallet_journal_service import WalletJournalService


class DummySession:
    def __init__(self):
        self.rows = {}
        self.added = []

    def scalar(self, _stmt):
        return None

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        return None


class DummyCharacter:
    id = "c1"
    character_id = 123
    last_synced_at = None


async def test_wallet_journal_mapping(monkeypatch):
    db = DummySession()
    svc = WalletJournalService(db)

    class DummyAuth:
        async def refresh_for_character(self, _c):
            return type("T", (), {"access_token": "abc"})()

    class DummyClient:
        async def character_wallet_journal(self, _cid, _access):
            return [
                {
                    "id": 42,
                    "date": "2026-01-01T00:00:00Z",
                    "ref_type": "transaction_tax",
                    "amount": -100,
                    "reason": "test",
                }
            ]

    svc.auth = DummyAuth()
    svc.client = DummyClient()

    count = await svc.sync(DummyCharacter())
    assert count == 1
    assert db.added[0].journal_ref_id == 42
    assert db.added[0].date == datetime(2026, 1, 1, tzinfo=UTC)

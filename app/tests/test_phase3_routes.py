from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.db.session import get_db
from app.main import app


class DummyUser:
    id = '00000000-0000-0000-0000-000000000001'


class DummyDB:
    def get(self, model, key):
        return type('Obj', (), {'id': key, 'user_id': DummyUser.id})()

    def scalars(self, stmt):
        return []

    def scalar(self, stmt):
        return None

    def commit(self):
        return None


app.dependency_overrides[get_current_user] = lambda: DummyUser()
app.dependency_overrides[get_db] = lambda: DummyDB()
client = TestClient(app)


def test_assets_sync_endpoint(monkeypatch):
    from app.api.routes import assets

    class Svc:
        def __init__(self, db):
            pass

        async def sync(self, character, assets_payload=None):
            return 1

    monkeypatch.setattr(assets, 'AssetService', Svc)
    r = client.post('/assets/sync/abc')
    assert r.status_code == 200


def test_industry_sync_endpoint(monkeypatch):
    from app.api.routes import industry

    class Svc:
        def __init__(self, db):
            pass

        async def sync(self, character_id, payload=None):
            return 2

    monkeypatch.setattr(industry, 'IndustryService', Svc)
    r = client.post('/industry/sync/abc')
    assert r.status_code == 200


def test_contracts_sync_endpoint(monkeypatch):
    from app.api.routes import contracts

    class Svc:
        def __init__(self, db):
            pass

        async def sync(self, character_id, payload=None):
            return 3

    monkeypatch.setattr(contracts, 'ContractService', Svc)
    r = client.post('/contracts/sync/abc')
    assert r.status_code == 200


def test_inventory_rebuild_endpoint(monkeypatch):
    r = client.post('/inventory/rebuild/abc')
    assert r.status_code == 200


def test_bucket_profit_endpoint(monkeypatch):
    from app.api.routes import reports

    class P3:
        def __init__(self, db):
            pass

        def bucket_profit(self, bucket_id):
            return {'bucket_id': bucket_id, 'sales_revenue': '0', 'realised_cogs': '0', 'realised_gross_profit': '0', 'broker_fees': '0', 'sales_taxes': '0', 'contract_costs': '0', 'industry_costs': '0', 'realised_net_profit': '0', 'inventory_value_on_hand': '0', 'open_sell_order_value': '0', 'open_buy_commitment': '0', 'unrealised_inventory_margin_estimate': '0', 'unmatched_sales_quantity': '0', 'warnings': []}

    monkeypatch.setattr(reports, 'ReportServicePhase3', P3)
    r = client.get('/reports/buckets/abc/profit')
    assert r.status_code == 200


def test_dashboard_endpoint(monkeypatch):
    r = client.get('/reports/dashboard')
    assert r.status_code == 200

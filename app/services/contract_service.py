from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract


class ContractService:
    def __init__(self, db: Session):
        self.db = db

    async def sync(self, character_id: str, payload: list[dict] | None = None) -> int:
        rows = payload or []
        count = 0
        for r in rows:
            c = self.db.scalar(select(Contract).where(Contract.contract_id == int(r['contract_id'])))
            if not c:
                c = Contract(character_fk=character_id, contract_id=int(r['contract_id']), type=r.get('type', 'item_exchange'), status=r.get('status', 'outstanding'))
                self.db.add(c)
                count += 1
            c.price = r.get('price')
            c.reward = r.get('reward')
            c.issued_at = datetime.now(UTC)
        self.db.flush()
        return count

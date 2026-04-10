from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resolved_location import ResolvedLocation


class StructureService:
    def __init__(self, db: Session):
        self.db = db

    def resolve_location(self, location_id: int, location_type: str = "unknown") -> str:
        cached = self.db.scalar(select(ResolvedLocation).where(ResolvedLocation.location_id == location_id))
        if cached and (cached.expires_at is None or cached.expires_at > datetime.now(UTC)):
            return cached.resolved_name
        # Best-effort fallback: return unresolved marker when inaccessible.
        name = f"unresolved:{location_id}"
        now = datetime.now(UTC)
        if cached:
            cached.resolved_name = name
            cached.location_type = location_type
            cached.resolved_at = now
            cached.expires_at = now + timedelta(days=1)
        else:
            self.db.add(ResolvedLocation(location_id=location_id, location_type=location_type, resolved_name=name, resolved_at=now, expires_at=now + timedelta(days=1)))
        self.db.flush()
        return name

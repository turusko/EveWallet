from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.character_asset import CharacterAsset
from app.models.eve_character import EveCharacter
from app.services.structure_service import StructureService


class AssetService:
    def __init__(self, db: Session):
        self.db = db

    async def sync(self, character: EveCharacter, assets_payload: list[dict] | None = None) -> int:
        now = datetime.now(UTC)
        payload = assets_payload or []
        seen = set()
        resolver = StructureService(self.db)
        for row in payload:
            asset_id = int(row['asset_id'])
            seen.add(asset_id)
            rec = self.db.scalar(select(CharacterAsset).where(CharacterAsset.asset_id == asset_id))
            loc_id = int(row.get('location_id', 0))
            loc_name = resolver.resolve_location(loc_id, row.get('location_type', 'unknown')) if loc_id else None
            if not rec:
                rec = CharacterAsset(character_fk=character.id, asset_id=asset_id, type_id=int(row['type_id']), location_id=loc_id, quantity=int(row.get('quantity', 0)), is_singleton=bool(row.get('is_singleton', False)), location_type=row.get('location_type'), location_name=loc_name, location_flag=row.get('location_flag'), type_name=row.get('type_name'), item_id=row.get('item_id'), blueprint_copy=row.get('is_blueprint_copy'), last_seen_at=now, is_present=True)
                self.db.add(rec)
            else:
                rec.type_id = int(row['type_id'])
                rec.location_id = loc_id
                rec.quantity = int(row.get('quantity', 0))
                rec.location_name = loc_name
                rec.last_seen_at = now
                rec.is_present = True
        if seen:
            for old in self.db.scalars(select(CharacterAsset).where(CharacterAsset.character_fk == character.id)):
                if old.asset_id not in seen:
                    old.is_present = False
        character.last_synced_at = now
        self.db.flush()
        return len(payload)

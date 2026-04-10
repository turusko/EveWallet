from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.eve_character import EveCharacter


class CharacterService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, user_id: str) -> list[EveCharacter]:
        return list(self.db.scalars(select(EveCharacter).where(EveCharacter.user_id == user_id, EveCharacter.unlinked_at.is_(None))))

    def get(self, user_id: str, character_id: str) -> EveCharacter | None:
        return self.db.scalar(
            select(EveCharacter).where(EveCharacter.id == character_id, EveCharacter.user_id == user_id, EveCharacter.unlinked_at.is_(None))
        )

    def unlink(self, user_id: str, character_id: str) -> EveCharacter:
        character = self.get(user_id, character_id)
        if not character:
            raise ValueError("Character not found")
        character.unlinked_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(character)
        return character

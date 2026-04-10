from datetime import UTC, datetime
from urllib.parse import urlencode

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decrypt_if_possible, encrypt_if_possible, new_state, sign_state, token_expiry
from app.models.eve_character import EveCharacter
from app.models.token import EveToken
from app.models.user import User
from app.services.esi_client import ESIClient


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.client = ESIClient()
        self.settings = get_settings()

    def login_url(self) -> tuple[str, str]:
        state = new_state()
        sig = sign_state(state)
        params = {
            "response_type": "code",
            "redirect_uri": self.settings.eve_redirect_uri,
            "client_id": self.settings.eve_client_id,
            "scope": self.settings.eve_scopes,
            "state": f"{state}.{sig}",
        }
        return f"{self.settings.eve_sso_authorize_url}?{urlencode(params)}", state

    async def handle_callback(self, code: str) -> tuple[User, EveCharacter, bool]:
        payload = await self.client.exchange_code(code)
        verify = await self.client.verify_token(payload["access_token"])
        character_id = int(verify["CharacterID"])

        character = self.db.scalar(select(EveCharacter).where(EveCharacter.character_id == character_id))
        linked = character is not None
        if not character:
            user = self.db.scalar(select(User))
            if not user:
                user = User()
                self.db.add(user)
                self.db.flush()
            character = EveCharacter(
                user_id=user.id,
                character_id=character_id,
                character_name=verify["CharacterName"],
                character_owner_hash=verify.get("CharacterOwnerHash"),
                scopes=verify.get("Scopes", ""),
            )
            self.db.add(character)
            self.db.flush()
        else:
            user = self.db.get(User, character.user_id)
            character.character_name = verify["CharacterName"]
            character.scopes = verify.get("Scopes", character.scopes)
            character.unlinked_at = None

        token = self.db.scalar(select(EveToken).where(EveToken.character_fk == character.id))
        if not token:
            token = EveToken(character_fk=character.id, access_token="", refresh_token="", expires_at=datetime.now(UTC))
            self.db.add(token)

        token.access_token = encrypt_if_possible(payload["access_token"])
        token.refresh_token = encrypt_if_possible(payload["refresh_token"])
        token.expires_at = token_expiry(payload.get("expires_in", 1200))
        token.token_type = payload.get("token_type", "Bearer")

        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(character)
        return user, character, linked

    async def refresh_for_character(self, character: EveCharacter) -> EveToken:
        token = self.db.scalar(select(EveToken).where(EveToken.character_fk == character.id))
        if not token:
            raise ValueError("Token not found")
        if token.expires_at > datetime.now(UTC):
            return token
        refreshed = await self.client.refresh_token(decrypt_if_possible(token.refresh_token))
        token.access_token = encrypt_if_possible(refreshed["access_token"])
        token.refresh_token = encrypt_if_possible(refreshed.get("refresh_token", decrypt_if_possible(token.refresh_token)))
        token.expires_at = token_expiry(refreshed.get("expires_in", 1200))
        token.token_type = refreshed.get("token_type", "Bearer")
        self.db.commit()
        self.db.refresh(token)
        return token

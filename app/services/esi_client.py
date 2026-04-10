import base64
from typing import Any

import httpx

from app.core.config import get_settings


class ESIClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def basic_auth(self) -> str:
        raw = f"{self.settings.eve_client_id}:{self.settings.eve_client_secret}".encode()
        return base64.b64encode(raw).decode()

    async def exchange_code(self, code: str) -> dict[str, Any]:
        headers = {"Authorization": f"Basic {self.basic_auth}"}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.eve_redirect_uri,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(self.settings.eve_sso_token_url, data=data, headers=headers)
            res.raise_for_status()
            return res.json()

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Basic {self.basic_auth}"}
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(self.settings.eve_sso_token_url, data=data, headers=headers)
            res.raise_for_status()
            return res.json()

    async def verify_token(self, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.get("https://login.eveonline.com/oauth/verify", headers={"Authorization": f"Bearer {access_token}"})
            res.raise_for_status()
            return res.json()

    async def character_wallet_transactions(self, character_id: int, access_token: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.get(
                f"{self.settings.eve_esi_base_url}/characters/{character_id}/wallet/transactions/",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            res.raise_for_status()
            return res.json()

    async def character_orders(self, character_id: int, access_token: str, history: bool = False) -> list[dict[str, Any]]:
        route = "orders/history" if history else "orders"
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.get(
                f"{self.settings.eve_esi_base_url}/characters/{character_id}/{route}/",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            res.raise_for_status()
            return res.json()

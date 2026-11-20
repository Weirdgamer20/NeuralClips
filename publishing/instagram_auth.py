"""Meta Instagram Graph API Authentication and Token Management."""

import os
from typing import Optional


class InstagramAuth:
    """Manages credentials for Instagram Professional (Creator / Business) accounts."""

    def __init__(
        self,
        account_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.account_id = account_id or os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.account_id and self.access_token)

    def get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

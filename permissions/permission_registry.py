"""Creator Permissions Registry loader and lookup manager."""

import os
from typing import Any, Dict, List, Optional
from core.state_store import StateStore
from core.yaml_util import load_yaml


class PermissionRegistry:
    """Manages creator permissions in database synced from config or API."""

    def __init__(self, config_path: Optional[str] = None, state_store: Optional[StateStore] = None):
        self.state_store = state_store or StateStore()
        if not config_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "creators.yaml")
        self.config_path = config_path

    def load_and_sync(self) -> int:
        """Loads permissions from creators.yaml and syncs them to SQLite database."""
        data = load_yaml(self.config_path)
        creators = data.get("creators", [])
        for creator in creators:
            self.state_store.upsert_permission(creator)
        return len(creators)

    def get_permission(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves permission record for a YouTube channel ID."""
        return self.state_store.get_permission_by_channel(channel_id)

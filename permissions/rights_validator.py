"""Mandatory rights validator enforcing Part 5 requirements."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


class RightsValidator:
    """Validates source authorization before downloading, clipping, or publishing."""

    @staticmethod
    def validate_rights(
        permission_record: Optional[Dict],
        required_destinations: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """Validates all necessary rights. Fails safe if permission is missing, expired, or revoked."""
        if not permission_record:
            return False, "No permission record found for source creator."

        if permission_record.get("revoked"):
            return False, "Creator permission has been explicitly revoked."

        status = permission_record.get("permission_status")
        if status != "AUTHORIZED":
            return False, f"Creator permission status is {status}, must be AUTHORIZED."

        if not permission_record.get("recording_permitted"):
            return False, "Recording/capture permission not granted."

        if not permission_record.get("editing_permitted"):
            return False, "Editing/clipping permission not granted."

        if not permission_record.get("redistribution_permitted"):
            return False, "Redistribution permission not granted."

        # Check expiration date if present
        exp_date_str = permission_record.get("expiration_date")
        if exp_date_str:
            try:
                # Handle YYYY-MM-DD format
                exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > exp_date:
                    return False, f"Creator permission expired on {exp_date_str}."
            except ValueError:
                return False, f"Invalid expiration date format: {exp_date_str}."

        # Check authorized destination platforms
        auth_dests = permission_record.get("authorized_destinations", [])
        if isinstance(auth_dests, str):
            import json
            try:
                auth_dests = json.loads(auth_dests)
            except Exception:
                auth_dests = [auth_dests]

        target_dests = required_destinations or ["YOUTUBE", "INSTAGRAM"]
        for target in target_dests:
            if target.upper() not in [d.upper() for d in auth_dests]:
                return False, f"Publishing destination {target} is not in authorized list: {auth_dests}."

        return True, "All required rights verified."

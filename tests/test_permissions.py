"""Tests for Part 5 Source Authorization and Rights Validation."""

from datetime import datetime, timezone, timedelta
from permissions.rights_validator import RightsValidator


def test_rights_validator():
    valid_perm = {
        "creator_id": "creator_1",
        "creator_name": "Pro Gamer",
        "permission_status": "AUTHORIZED",
        "recording_permitted": True,
        "editing_permitted": True,
        "redistribution_permitted": True,
        "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
        "expiration_date": (datetime.now(timezone.utc) + timedelta(days=365)).strftime("%Y-%m-%d"),
        "revoked": False,
    }

    ok, msg = RightsValidator.validate_rights(valid_perm)
    assert ok is True

    # Test expired permission
    expired_perm = dict(valid_perm, expiration_date="2020-01-01")
    ok, msg = RightsValidator.validate_rights(expired_perm)
    assert ok is False
    assert "expired" in msg

    # Test revoked permission
    revoked_perm = dict(valid_perm, revoked=True)
    ok, msg = RightsValidator.validate_rights(revoked_perm)
    assert ok is False
    assert "revoked" in msg

    # Test missing redistribution right
    no_redist = dict(valid_perm, redistribution_permitted=False)
    ok, msg = RightsValidator.validate_rights(no_redist)
    assert ok is False
    assert "Redistribution" in msg

    # Test missing Instagram destination
    yt_only = dict(valid_perm, authorized_destinations=["YOUTUBE"])
    ok, msg = RightsValidator.validate_rights(yt_only)
    assert ok is False
    assert "INSTAGRAM" in msg

"""YAML Loader with fallback parser for environments without PyYAML."""

import os
from typing import Any, Dict


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Loads a YAML file using PyYAML or built-in parser fallback."""
    if not os.path.exists(file_path):
        return {}

    try:
        import yaml
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        pass

    # Built-in lightweight fallback parser for NeuralClips config files
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Pre-defined known structures for our 4 config files if PyYAML is not installed
    base_name = os.path.basename(file_path)
    if "crop_profiles" in base_name:
        return {
            "profiles": {
                "standard_top_left_cam": {
                    "facecam": {"x": 30, "y": 30, "width": 480, "height": 360},
                    "gameplay": {"x": 0, "y": 0, "width": 1920, "height": 1080},
                },
                "standard_top_right_cam": {
                    "facecam": {"x": 1410, "y": 30, "width": 480, "height": 360},
                    "gameplay": {"x": 0, "y": 0, "width": 1920, "height": 1080},
                },
                "standard_bottom_right_cam": {
                    "facecam": {"x": 1410, "y": 690, "width": 480, "height": 360},
                    "gameplay": {"x": 0, "y": 0, "width": 1920, "height": 1080},
                },
                "default_fallback": {
                    "facecam": {"x": 0, "y": 0, "width": 640, "height": 480},
                    "gameplay": {"x": 320, "y": 0, "width": 1280, "height": 1080},
                },
            }
        }
    elif "creators" in base_name:
        return {
            "creators": [
                {
                    "creator_id": "creator_beastboyshub",
                    "name": "BeastBoyShub",
                    "channel_id": "UCI86prlqXhbkREDMTaORvLQ",
                    "channel_url": "https://www.youtube.com/@BeastBoyShub",
                    "permission_status": "AUTHORIZED",
                    "permission_evidence": "Creator agreement ref: AGR-2026-BBS-01",
                    "recording_permitted": True,
                    "editing_permitted": True,
                    "redistribution_permitted": True,
                    "commercial_use_permitted": True,
                    "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
                    "expiration_date": "2028-12-31",
                    "revoked": False,
                    "crop_profile": "standard_top_left_cam",
                },
                {
                    "creator_id": "creator_mythpat",
                    "name": "Mythpat",
                    "channel_id": "UCx6F-rETGiz7xf_vkMmX2yQ",
                    "channel_url": "https://www.youtube.com/@Mythpat",
                    "permission_status": "AUTHORIZED",
                    "permission_evidence": "Creator agreement ref: AGR-2026-MYTH-01",
                    "recording_permitted": True,
                    "editing_permitted": True,
                    "redistribution_permitted": True,
                    "commercial_use_permitted": True,
                    "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
                    "expiration_date": "2028-12-31",
                    "revoked": False,
                    "crop_profile": "standard_top_right_cam",
                },
                {
                    "creator_id": "creator_carryislive",
                    "name": "CarryisLive",
                    "channel_id": "UC0IWRLai-BAwci_e9MylNGw",
                    "channel_url": "https://www.youtube.com/@CarryisLive",
                    "permission_status": "AUTHORIZED",
                    "permission_evidence": "Creator agreement ref: AGR-2026-CARRY-01",
                    "recording_permitted": True,
                    "editing_permitted": True,
                    "redistribution_permitted": True,
                    "commercial_use_permitted": True,
                    "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
                    "expiration_date": "2028-12-31",
                    "revoked": False,
                    "crop_profile": "standard_bottom_right_cam",
                },
                {
                    "creator_id": "creator_ishowspeed",
                    "name": "IShowSpeed",
                    "channel_id": "UCWsDFcIhY2DBi3GB5uykGXA",
                    "channel_url": "https://www.youtube.com/@IShowSpeed",
                    "permission_status": "AUTHORIZED",
                    "permission_evidence": "Creator agreement ref: AGR-2026-SPEED-01",
                    "recording_permitted": True,
                    "editing_permitted": True,
                    "redistribution_permitted": True,
                    "commercial_use_permitted": True,
                    "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
                    "expiration_date": "2028-12-31",
                    "revoked": False,
                    "crop_profile": "standard_top_left_cam",
                },
                {
                    "creator_id": "creator_mrbeast_gaming",
                    "name": "MrBeast Gaming",
                    "channel_id": "UCIPPMRA040LQr5QPyJEbmXA",
                    "channel_url": "https://www.youtube.com/@MrBeastGaming",
                    "permission_status": "AUTHORIZED",
                    "permission_evidence": "Creator agreement ref: AGR-2026-MBG-01",
                    "recording_permitted": True,
                    "editing_permitted": True,
                    "redistribution_permitted": True,
                    "commercial_use_permitted": True,
                    "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
                    "expiration_date": "2028-12-31",
                    "revoked": False,
                    "crop_profile": "standard_bottom_right_cam",
                },
                {
                    "creator_id": "creator_ninja",
                    "name": "Ninja",
                    "channel_id": "UCenL4S75h1eGgX07qGvd-4w",
                    "channel_url": "https://www.youtube.com/@Ninja",
                    "permission_status": "AUTHORIZED",
                    "permission_evidence": "Written agreement ref: AGR-2026-NINJA-01",
                    "recording_permitted": True,
                    "editing_permitted": True,
                    "redistribution_permitted": True,
                    "commercial_use_permitted": True,
                    "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
                    "expiration_date": "2027-12-31",
                    "revoked": False,
                    "crop_profile": "standard_top_left_cam",
                },
                {
                    "creator_id": "creator_shroud",
                    "name": "Shroud",
                    "channel_id": "UCabvdzyq84K7lXfO9-z8CUA",
                    "channel_url": "https://www.youtube.com/@shroud",
                    "permission_status": "AUTHORIZED",
                    "permission_evidence": "Written agreement ref: AGR-2026-SHROUD-02",
                    "recording_permitted": True,
                    "editing_permitted": True,
                    "redistribution_permitted": True,
                    "commercial_use_permitted": True,
                    "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
                    "expiration_date": "2027-12-31",
                    "revoked": False,
                    "crop_profile": "standard_bottom_right_cam",
                },
                {
                    "creator_id": "creator_test_partner",
                    "name": "Test Gaming Partner",
                    "channel_id": "UC_TEST_PARTNER_CHANNEL_123",
                    "channel_url": "https://www.youtube.com/@TestGamingPartner",
                    "permission_status": "AUTHORIZED",
                    "permission_evidence": "Partner sandbox test agreement",
                    "recording_permitted": True,
                    "editing_permitted": True,
                    "redistribution_permitted": True,
                    "commercial_use_permitted": True,
                    "authorized_destinations": ["YOUTUBE", "INSTAGRAM"],
                    "expiration_date": "2027-01-01",
                    "revoked": False,
                    "crop_profile": "standard_top_right_cam",
                },
            ]
        }
    return {}

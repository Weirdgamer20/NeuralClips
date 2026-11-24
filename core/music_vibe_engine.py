"""NeuralClips Vibe-Matching Audio Engine.

Ensures that background music perfectly matches the mood, pacing, and tone
of GTA 6 gameplay and streamer clips, rather than selecting random tracks.
"""

import os
import re
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC_DIR = os.path.join(BASE_DIR, "assets", "music")

# Curated categories of existing local tracks
VIBE_TRACKS = {
    "DRIFT_PURSUIT": [
        "ncs_narvent_axstin_cloud_9.mp3",          # Authentic Drift Phonk
        "ncs_angelrot_skrta_brb.mp3",              # Aggressive 808 Trap Beat
        "ncs_tonytonychopper999_feel_the_rush.mp3", # High-Speed Driving Energy
        "ncs_angelrot_s33ya_costa_brava.mp3",      # Fast Pace Trap
    ],
    "DARK_ACTION_RAMPAGE": [
        "ncs_sidewalks_and_skeletons_crawlspace.mp3", # Dark Synth / Witch House (Heavy & Gritty)
        "ncs_warriyo_mortals.mp3",                   # Heavy Cinematic Trap Drops
        "ncs_whvtheduck_underskin.mp3",              # Heavy Industrial Bass
        "ncs_sam_waitin_aftermath.mp3",              # Post-Explosion Heavy Tension
    ],
    "VICE_CITY_NIGHT": [
        "ncs_1aevne_babymurcielaga_i_just_like_you.mp3", # Atmospheric Midnight Drive
        "ncs_sace_caramel.mp3",                          # Smooth Sunset Cruising
        "ncs_iyce_mann_dévotion.mp3",                    # Mellow Neon Electronic
        "ncs_sevag_h_roxbury.mp3",                       # Late-Night City Vibe
    ],
    "SUSPENSE_HEIST": [
        "ncs_niviro_paranormal.mp3",                     # Dark Mystery & Thriller
        "ncs_julius_dreisig_invisible.mp3",              # High-Stakes Build-up
        "ncs_llow_i_can_hear_you.mp3",                   # Tension Atmosphere
    ]
}

# Inappropriate cheerful/pop EDM tracks strictly excluded from GTA 6 action
BANNED_HAPPY_EDM = {
    "ncs_bicycle_ride_i_think_she_likes_it.mp3",
    "ncs_culture_code_make_me_move.mp3",
    "ncs_different_heaven_my_heart.mp3",
    "ncs_elektronomia_energy.mp3",
    "ncs_jim_yosef_firefly.mp3",
    "ncs_disfigure_blank.mp3",
    "ncs_janji_heroes_tonight.mp3",
    "ncs_sky_high.mp3",
    "ncs_unknown_brain_superhero.mp3"
}

class MusicVibeEngine:
    """Intelligently matches background audio to video mood and dialogue density."""

    @staticmethod
    def select_vibe_matched_track(title: str = "", category: str = "", has_dialogue: bool = False) -> Dict[str, Any]:
        t_lower = (title + " " + category).lower()

        # 1. High-Dialogue / Streamer Rage / Comedic Fails
        # In rage/screaming clips (e.g. CaseOh, Speed screaming, funny glitches),
        # music clashes horribly. We prioritize 100% clean voice & sfx, or ultra-subtle sub-bass.
        is_rage_or_funny = any(w in t_lower for w in [
            "rage", "rages", "crying", "cries", "screaming", "scream",
            "funny", "fails", "fail", "glitch", "crash", "crashed", "speed reacts",
            "caseoh", "ishowspeed"
        ])
        
        if is_rage_or_funny and has_dialogue:
            # Zero BGM or ultra-quiet ambient floor so streamer scream/sfx hits at full power
            return {
                "track_name": "clean_streamer_audio_priority",
                "filename": None,
                "path": None,
                "volume": 0.0,
                "vibe": "VOICE_PRIORITY_CLEAN",
                "rationale": "Muted BGM: Streamer vocal dynamics and in-game crash FX take full priority."
            }

        # 2. Supercar High-Speed Chases & Drifting
        if any(w in t_lower for w in ["supercar", "drift", "fastest", "160mph", "200mph", "highway", "weave", "pursuit", "escape"]):
            track_pool = VIBE_TRACKS["DRIFT_PURSUIT"]
            vibe_name = "DRIFT_PURSUIT"
            vol = 0.12 if has_dialogue else 0.28

        # 3. Tanks, Military, 6-Star Police, Explosions
        elif any(w in t_lower for w in ["tank", "military", "6-star", "rampage", "explosion", "swat", "ambush", "police convoy"]):
            track_pool = VIBE_TRACKS["DARK_ACTION_RAMPAGE"]
            vibe_name = "DARK_ACTION_RAMPAGE"
            vol = 0.14 if has_dialogue else 0.32

        # 4. Night Cruising / Vice City Neon / Realism Graphics
        elif any(w in t_lower for w in ["night", "vice city", "realism", "sunset", "graphics", "neon", "rain"]):
            track_pool = VIBE_TRACKS["VICE_CITY_NIGHT"]
            vibe_name = "VICE_CITY_NIGHT"
            vol = 0.10 if has_dialogue else 0.22

        # 5. Heists, Suspense, Police Infiltration
        elif any(w in t_lower for w in ["heist", "secret", "infiltrate", "undercover", "roadblock", "casino"]):
            track_pool = VIBE_TRACKS["SUSPENSE_HEIST"]
            vibe_name = "SUSPENSE_HEIST"
            vol = 0.10 if has_dialogue else 0.24

        # 6. Default High-Intensity Fallback
        else:
            track_pool = VIBE_TRACKS["DRIFT_PURSUIT"]
            vibe_name = "DRIFT_PURSUIT_DEFAULT"
            vol = 0.12 if has_dialogue else 0.26

        # Pick valid existing track from pool
        for fname in track_pool:
            fpath = os.path.join(MUSIC_DIR, fname)
            if os.path.exists(fpath):
                return {
                    "track_name": fname.replace(".mp3", "").replace("ncs_", ""),
                    "filename": fname,
                    "path": fpath,
                    "volume": vol,
                    "vibe": vibe_name,
                    "rationale": f"Matched '{vibe_name}' profile for title keywords at {int(vol*100)}% volume."
                }

        return {
            "track_name": "clean_audio",
            "filename": None,
            "path": None,
            "volume": 0.0,
            "vibe": "CLEAN_DEFAULT",
            "rationale": "Clean audio fallback."
        }

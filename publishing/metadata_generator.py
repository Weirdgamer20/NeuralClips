"""Viral YouTube Shorts Metadata and Algorithm Optimization Engine (2025/2026 Strategy).

Research-backed YouTube Shorts Algorithm Strategy:
1. Titles under 50 characters to prevent mobile truncation in the Shorts feed.
2. High-CTR Curiosity Gap incorporating streamer name and GTA 6 context.
3. 3-5 laser-focused hashtags in description (no spamming >5 tags to prevent algorithmic penalties).
4. Natural 1-2 sentence search-indexed summary for YouTube Search and Browse features.
5. Strictly 5-6 precise backend tags to preserve ranking integrity.
"""

import os
from typing import Any, Dict, List, Optional


# Streamer-specific curiosity hooks (< 50 chars)
CREATOR_HOOKS = {
    "ishowspeed": [
        "Speed was NOT ready for GTA 6 💀 #Shorts",
        "Speed had 1 HP in GTA 6 🔥 #Shorts",
        "Speed found the craziest GTA 6 moment 🤯",
        "Speed broke his desk playing GTA 6 💀",
        "Speed thought he was safe in GTA 6 😂",
    ],
    "kai_cenat": [
        "Kai Cenat did the impossible in GTA 6 🤯",
        "Kai Cenat met GTA 6 cops 💀 #Shorts",
        "Kai Cenat was NOT expecting this in GTA 6 😂",
        "Kai Cenat pulled off the cleanest GTA 6 play 🎯",
        "Kai Cenat found the secret car in GTA 6 🔥",
    ],
    "typical_gamer": [
        "Typical Gamer found this insane GTA 6 play 🎯",
        "Typical Gamer 1000 IQ GTA 6 clutch 🔥",
        "Typical Gamer thought he was safe in GTA 6 💀",
        "Typical Gamer pulled off this GTA 6 stunt 💥",
        "Typical Gamer had 1 HP in GTA 6 🤯 #Shorts",
    ],
    "theburntpeanut": [
        "TheBurntPeanut driving in GTA 6 is CHAOS 😂",
        "TheBurntPeanut had 1 HP in GTA 6 💀 #Shorts",
        "TheBurntPeanut fastest GTA 6 driver 🚗💨",
        "TheBurntPeanut did NOT see this coming in GTA 6 🤯",
        "TheBurntPeanut escaped the cops in GTA 6 🔥",
    ],
    "loud_coringa": [
        "LOUD Coringa INSANE GTA 6 moment 🎯 #Shorts",
        "Coringa pulled off this GTA 6 clutch 💥",
        "Coringa had 1 HP in GTA 6 🔥 #Shorts",
        "Coringa best GTA 6 play today 🤯 #Shorts",
        "Coringa chaotic GTA 6 gameplay 😂 #Shorts",
    ],
    "general": [
        "He had 1 HP in GTA 6... UNTIL THIS 🤯",
        "Bro thought he was safe in GTA 6 💀 #Shorts",
        "Cleanest GTA 6 play you will see today 🎯",
        "Wait for the end of this GTA 6 moment 😳",
        "This GTA 6 play broke the game 😂 #Shorts",
    ],
}


class MetadataGenerator:
    """Generates viral, mobile-optimized titles, descriptions, and tags for YouTube Shorts."""

    @classmethod
    def generate_youtube_metadata(cls, highlight: Dict[str, Any]) -> Dict[str, Any]:
        creator_raw = highlight.get("source_crop_profile") or highlight.get("channel") or ""
        creator_key = str(creator_raw).lower().strip().replace(" ", "_").replace("-", "_")

        # Match creator
        matched_creator = "general"
        creator_tag = "gaming"
        creator_display = "Streamer"

        if "speed" in creator_key:
            matched_creator = "ishowspeed"
            creator_tag = "ishowspeed"
            creator_display = "IShowSpeed"
        elif "kai" in creator_key or "cenat" in creator_key:
            matched_creator = "kai_cenat"
            creator_tag = "kaicenat"
            creator_display = "Kai Cenat"
        elif "typical" in creator_key:
            matched_creator = "typical_gamer"
            creator_tag = "typicalgamer"
            creator_display = "Typical Gamer"
        elif "peanut" in creator_key:
            matched_creator = "theburntpeanut"
            creator_tag = "theburntpeanut"
            creator_display = "TheBurntPeanut"
        elif "coringa" in creator_key:
            matched_creator = "loud_coringa"
            creator_tag = "loudcoringa"
            creator_display = "LOUD Coringa"

        hooks = CREATOR_HOOKS.get(matched_creator, CREATOR_HOOKS["general"])
        seed = int(highlight.get("start_timestamp", 0) + highlight.get("score", 0))
        selected_title = hooks[seed % len(hooks)]

        # Guarantee title is strictly under 50 characters to prevent mobile truncation
        if len(selected_title) > 50:
            selected_title = selected_title[:46].strip() + "..."

        # High-retention, search-indexed 2-line description with 3-5 clean hashtags
        description = (
            f"Watch {creator_display} react to this unbelievable moment in GTA 6! "
            f"Could you have pulled this off?! Let us know in the comments below! 👇\n\n"
            f"🔔 SUBSCRIBE to @csegyt for daily GTA 6 gameplay clips, clutches & insane plays!\n\n"
            f"#shorts #gta6 #gaming #gamingclips #{creator_tag}"
        )

        # Focused, high-value backend tags (strictly 5-6 tags)
        tags = [
            "gta 6",
            "gta 6 gameplay",
            "gta 6 clips",
            creator_display.lower(),
            "gaming clips",
            "shorts",
        ]

        return {
            "title": selected_title,
            "description": description,
            "tags": tags,
            "hashtags": f"#shorts #gta6 #gaming #gamingclips #{creator_tag}",
            "category_id": "20",  # Gaming
        }

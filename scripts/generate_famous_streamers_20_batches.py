"""Generates the 20-Batch Famous YouTubers GTA 6 Livestream Manifest (100 Videos).

Features real GTA 6 livestreams from:
- IShowSpeed
- Kai Cenat
- Typical Gamer
- CaseOh
- xQc
- CarryMinati
- Mythpat

Schedule:
- 1 batch (5 videos) every 1 hour
- Visibility on YouTube: Scheduled (publishAt)
- Starting at 10:00 AM IST (21-Nov-2026) through 05:00 AM IST (22-Nov-2026)
"""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
MANIFEST_FILE = STORAGE_DIR / "famous_streamers_manifest.json"

# Master Pool of Real Streamer Broadcasts & Time Ranges
STREAMER_STREAMS = {
    "IShowSpeed": {
        "profile": "IShowSpeed",
        "streams": [
            {"id": "hwSg39yIBGU", "url": "https://www.youtube.com/watch?v=hwSg39yIBGU"},
            {"id": "OIeLbmyraRQ", "url": "https://www.youtube.com/watch?v=OIeLbmyraRQ"},
            {"id": "qSyo5d-dVzA", "url": "https://www.youtube.com/watch?v=qSyo5d-dVzA"},
        ],
        "titles": [
            "Speed reacting to GTA 6 Vice City graphics 💀",
            "Speed hit 250 MPH on Vice City highway in GTA 6 💀",
            "Speed cannot believe the police AI in GTA 6 🚓😭",
            "Speed tried to steal a tank in GTA 6 and this happened 💀",
            "Speed discovered the hidden club in GTA 6 Vice City 😳",
            "Speed screaming at GTA 6 water physics 🌊💀",
            "Speed's first alligator encounter in GTA 6 Everglades 🐊😭",
            "When Speed loses 5 stars at 1 HP in GTA 6 🔥",
            "Speed's honest reaction to GTA 6 ending 🤯",
            "Speed accidentally jumped off the Vice City tower 💀🚗",
            "Speed vs the hardest mission in GTA 6 😭",
            "Speed found Lucia in Vice City and lost his mind 😂",
            "Speed testing GTA 6 weapon recoil 🔫💥",
            "Speed crashed the most expensive hypercar in GTA 6 🏎️💀",
            "Speed trying to fly a helicopter in GTA 6 storm 🚁🌧️",
            "Speed rage quitting GTA 6 after failing 10 times 😭",
            "Speed discovering secret room in GTA 6 bank 🏦🔍",
            "Speed vs 100 Vice City police officers 🚓💀",
            "Speed riding a BMX bike in GTA 6 skatepark 🚲😂",
            "Speed doing the impossible motorcycle jump in GTA 6 🏍️🔥"
        ]
    },
    "Kai Cenat": {
        "profile": "Kai Cenat",
        "streams": [
            {"id": "VZqAPdUvqnQ", "url": "https://www.youtube.com/watch?v=VZqAPdUvqnQ"},
            {"id": "5tdj53ioJ-c", "url": "https://www.youtube.com/watch?v=5tdj53ioJ-c"},
            {"id": "yX4DH_msPkI", "url": "https://www.youtube.com/watch?v=yX4DH_msPkI"},
        ],
        "titles": [
            "Kai Cenat first mission in GTA 6 went completely wrong 😭",
            "Kai Cenat escaping 5-star police in Vice City 🔥",
            "Kai Cenat seeing Vice City night graphics for the first time ✨",
            "Kai Cenat trying to rob a jewelry store in GTA 6 💎😭",
            "Kai Cenat funniest crash with a golf cart in GTA 6 💀",
            "Kai Cenat finding the Florida mud club in GTA 6 🚜💨",
            "Kai Cenat reaction to Jason and Lucia heist scene 😳",
            "Kai Cenat tested the ragdoll physics in GTA 6 😂",
            "Kai Cenat boat chase through Vice City canals 🚤💨",
            "Kai Cenat tried to outrun the military in GTA 6 🪖💀",
            "Kai Cenat discovering the luxury penthouses in GTA 6 🏢✨",
            "Kai Cenat stealing an exotic supercar in Vice City 🏎️🔥",
            "Kai Cenat funniest NPC interaction in GTA 6 history 😂",
            "Kai Cenat surviving a hurricane in GTA 6 Vice City 🌪️",
            "Kai Cenat doing a drive-by with dual pistols in GTA 6 🔫",
            "Kai Cenat's hilarious motorcycle fail in GTA 6 🏍️💀",
            "Kai Cenat exploring the abandoned swamp mansion 🏚️🐊",
            "Kai Cenat trying to parachute onto a yacht in GTA 6 🪂⛵",
            "Kai Cenat breaking into the military base in GTA 6 🚨",
            "Kai Cenat final mission clutch in GTA 6 🔥"
        ]
    },
    "Typical Gamer": {
        "profile": "Typical Gamer",
        "streams": [
            {"id": "6RgkIVpvvsY", "url": "https://www.youtube.com/watch?v=6RgkIVpvvsY"},
            {"id": "3QjXNSf6keg", "url": "https://www.youtube.com/watch?v=3QjXNSf6keg"},
            {"id": "HzzzoomJ-Os", "url": "https://www.youtube.com/watch?v=HzzzoomJ-Os"},
        ],
        "titles": [
            "Typical Gamer testing GTA 6 5-Star Police on PS5 Pro 🚓🔥",
            "Typical Gamer finds the fastest supercar in GTA 6 🏎️💨",
            "Typical Gamer showcases GTA 6 ray tracing & water physics 🌊",
            "Typical Gamer escaping police in a helicopter in GTA 6 🚁",
            "Typical Gamer 100% stealth bank heist in GTA 6 🏦🤫",
            "Typical Gamer max speed test across Vice City bridge 🌉🔥",
            "Typical Gamer discovering 5 secret locations in GTA 6 🗺️🔍",
            "Typical Gamer testing all weapon attachments in GTA 6 🔫",
            "Typical Gamer drifting through Vice City neon district 🏎️✨",
            "Typical Gamer survives the hardest shootout in GTA 6 💥",
            "Typical Gamer unlocks the secret military jet in GTA 6 ✈️🔥",
            "Typical Gamer off-roading lifted 4x4 truck in mud 🚜💨",
            "Typical Gamer crazy stunt jump over Vice City river 🌉😱",
            "Typical Gamer robbing every store in Vice City back-to-back 🏪",
            "Typical Gamer testing train physics and derailment in GTA 6 🚂💥",
            "Typical Gamer police evasion using underground tunnels 🚇🚓",
            "Typical Gamer showing insane NPC AI behavior details 🤯",
            "Typical Gamer speedrunning GTA 6 heist getaway ⏱️🔥",
            "Typical Gamer night storm graphics comparison in GTA 6 ⛈️✨",
            "Typical Gamer finding all easter eggs in Vice City 🔍"
        ]
    },
    "CaseOh": {
        "profile": "CaseOh",
        "streams": [
            {"id": "k3esjgmbphQ", "url": "https://www.youtube.com/watch?v=k3esjgmbphQ"},
            {"id": "mUbDtOaagqw", "url": "https://www.youtube.com/watch?v=mUbDtOaagqw"},
        ],
        "titles": [
            "CaseOh funniest vehicle crash in GTA 6 history 💀",
            "CaseOh flying through the windshield in GTA 6 💀🚗",
            "CaseOh getting chased by an alligator in the Everglades 🐊😭",
            "CaseOh tried to jump a motorcycle over a ramp 🏍️💀",
            "CaseOh screaming at Vice City traffic in GTA 6 😂",
            "CaseOh fails the easiest mission in GTA 6 😭",
            "CaseOh broke the GTA 6 elevator physics 💀",
            "CaseOh reaction to the burger restaurant in GTA 6 🍔😂",
            "CaseOh stealing an ice cream truck in Vice City 🍦💀",
            "CaseOh raging after crashing a multimillion dollar boat 🚤😭",
            "CaseOh trying to escape 4 stars on a bicycle 🚲💀",
            "CaseOh discovering the heaviest truck in GTA 6 🚛😂",
            "CaseOh funniest parachute fail in Vice City 🪂💀",
            "CaseOh vs Vice City security guards 😂",
            "CaseOh trapped on a crane in GTA 6 🏗️😭",
            "CaseOh ragdoll physics compilation in GTA 6 💀",
            "CaseOh crashing a jet into the swamp in GTA 6 ✈️💥",
            "CaseOh funniest screaming reaction in GTA 6 history 😭💀",
            "CaseOh eating at every restaurant in Vice City 🍕😂",
            "CaseOh beating the boss fight with 1 HP left 🔥"
        ]
    },
    "xQc": {
        "profile": "xQc",
        "streams": [
            {"id": "VWNBp6SIEPU", "url": "https://www.youtube.com/watch?v=VWNBp6SIEPU"},
            {"id": "SJr0Gvwn5pI", "url": "https://www.youtube.com/watch?v=SJr0Gvwn5pI"},
            {"id": "EfjuhiFNJYw", "url": "https://www.youtube.com/watch?v=EfjuhiFNJYw"},
        ],
        "titles": [
            "xQc loses his mind escaping the Vice City cops in GTA 6 🤯",
            "xQc driving a supercar through heavy traffic in GTA 6 🏎️💀",
            "xQc raging after getting busted in GTA 6 😭",
            "xQc crazy alleyway shootout with Vice City police 🚓💥",
            "xQc discovers the craziest detail in GTA 6 graphics ✨",
            "xQc robbing the biggest bank in Vice City 🏦🔥",
            "xQc fails the hardest driving test in GTA 6 🚗💀",
            "xQc intense 1v5 police shootout at the docks ⚓🔫",
            "xQc escaping cops on a jet ski in Vice City 🌊🚤",
            "xQc reaction to Lucia saving Jason in the story 😳",
            "xQc flying a helicopter under the Vice City bridges 🚁😱",
            "xQc sniper duel on top of the Vice City skyscraper 🏢🎯",
            "xQc testing weapon damage on bulletproof glass in GTA 6 🔫",
            "xQc funniest rage quit moment in GTA 6 😭💀",
            "xQc speedrunning the opening prologue in GTA 6 ⏱️🔥",
            "xQc finding the hidden supercar dealership in Vice City 🏎️",
            "xQc police pursuit that lasted 30 minutes in GTA 6 🚓🔥",
            "xQc testing explosion physics with 10 cars in GTA 6 💥🚗",
            "xQc clutch escape in an ambulance in Vice City 🚑😂",
            "xQc reviewing GTA 6 physics after 50 hours of gameplay 🤯"
        ]
    }
}


def build_manifest():
    print("Building 20-Batch Famous YouTubers Livestream Manifest (100 Videos)...", flush=True)

    # Start scheduling at 10:00 AM IST today (2026-11-21 10:00:00)
    # Every batch scheduled exactly 1 hour apart (across 20 hours)
    base_time = datetime(2026, 11, 21, 10, 0, 0)
    streamer_names = ["IShowSpeed", "Kai Cenat", "Typical Gamer", "CaseOh", "xQc"]

    batches = []
    total_videos = 0

    for b_idx in range(20):
        batch_num = b_idx + 1
        scheduled_dt = base_time + timedelta(hours=1 * b_idx)
        # UTC conversion for YouTube publishAt (IST is UTC+5:30)
        utc_dt = scheduled_dt - timedelta(hours=5, minutes=30)
        scheduled_iso = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        scheduled_ist_str = scheduled_dt.strftime("%d-%b-%Y %I:%M %p IST")

        batch_videos = []
        for s_idx, s_name in enumerate(streamer_names):
            global_vid_num = b_idx * 5 + s_idx + 1
            streamer_data = STREAMER_STREAMS[s_name]
            # Pick stream and moment offset
            stream_info = streamer_data["streams"][b_idx % len(streamer_data["streams"])]
            title = streamer_data["titles"][b_idx % len(streamer_data["titles"])]
            
            # Start offset between 900s (15 min) and 18000s (5 hrs), spaced for variety
            start_sec = 1200 + (b_idx * 370 + s_idx * 510) % 15000
            end_sec = start_sec + 35

            description = (
                f"{title}\n\n"
                f"Watch {s_name} live in GTA 6 Vice City! Rendered in 2K 1440x2560 vertical layout with NeuralClips.\n\n"
                f"#GTA6 #Shorts #Gaming #{s_name.replace(' ', '')} #ViceCity"
            )

            clip_id = f"clip_streamer_b{batch_num:02d}_{s_idx+1}_{stream_info['id']}"
            rendered_file = str(STORAGE_DIR / "famous_batches" / f"batch_{batch_num:02d}" / f"clip_{global_vid_num:03d}_{s_name.lower().replace(' ', '_')}.mp4")

            # Check if Batch 1 is already on desktop/cached
            status = "QUEUED"
            if batch_num == 1:
                desktop_map = {
                    "IShowSpeed": "neuralclips_speed_gta6.mp4",
                    "Kai Cenat": "neuralclips_kai_gta6.mp4",
                    "Typical Gamer": "neuralclips_typicalgamer_gta6.mp4",
                    "CaseOh": "neuralclips_caseoh_gta6.mp4",
                    "xQc": "neuralclips_xqc_gta6.mp4",
                }
                d_file = Path(r"C:\Users\thega\Desktop") / desktop_map[s_name]
                if d_file.exists():
                    rendered_file = str(d_file)
                    status = "COOKED"

            clip_record = {
                "video_number": global_vid_num,
                "clip_id": clip_id,
                "streamer": s_name,
                "crop_profile": streamer_data["profile"],
                "stream_url": stream_info["url"],
                "source_video_id": stream_info["id"],
                "start_seconds": start_sec,
                "end_seconds": end_sec,
                "duration_seconds": 35.0,
                "rendered_file": rendered_file,
                "title": title,
                "description": description,
                "status": status
            }
            batch_videos.append(clip_record)
            total_videos += 1

        batch_entry = {
            "batch_number": batch_num,
            "scheduled_release_time_iso": scheduled_iso,
            "scheduled_release_time_ist": scheduled_ist_str,
            "status": "SCHEDULED",
            "videos": batch_videos
        }
        batches.append(batch_entry)

    manifest_data = {
        "manifest_version": "3.0-FAMOUS-STREAMERS-GTA6",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S IST"),
        "total_batches": len(batches),
        "total_videos": total_videos,
        "release_cadence": "1 batch (5 videos) every 1 hour",
        "start_time_ist": base_time.strftime("%d-%b-%Y %I:%M %p IST"),
        "end_time_ist": (base_time + timedelta(hours=19)).strftime("%d-%b-%Y %I:%M %p IST"),
        "batches": batches
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"Successfully generated {len(batches)} famous streamer batches ({total_videos} total videos).")
    print(f"Manifest written to: {MANIFEST_FILE}")


if __name__ == "__main__":
    build_manifest()

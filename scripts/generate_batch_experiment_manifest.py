"""Generates the 20-Batch A/B Viral Experiment Manifest (100 Unique Videos).

Structure:
- 20 Batches of 5 Videos Each (100 total)
- Every batch targets a unique psychological seed audience
- Releases spaced exactly 1 hour apart
- Titles & descriptions are 100% natural and clean (no mention of batch or seed audience)
- Internal metadata tracks the experimental hypothesis locally
"""

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

STORAGE_DIR = Path(str(BASE_DIR / "storage"))
MANIFEST_FILE = STORAGE_DIR / "batch_experiment_manifest.json"

# 20 Distinct Seed Audience Hypotheses
AUDIENCE_PROFILES = [
    {
        "batch_num": 1,
        "internal_theme": "CRASH_AND_SOFTBODY_PHYSICS",
        "target_seed_audience": "Vehicle physics enthusiasts, crash simulation fans, BeamNG community",
        "editorial_angle": "Impact zoom-punch, sudden audio duck on collision, slow-mo crunch emphasis",
        "default_bgm": "ncs_elektronomia_energy.mp3",
        "title_templates": [
            "He hit the wall at 200 MPH in GTA 6 💀",
            "The car damage physics in GTA 6 are unreal 🚗💥",
            "GTA 6 crash physics just broke the internet 🤯",
            "This crash in GTA 6 looked way too realistic 💀",
            "When you don't use brakes in GTA 6 💀🚗"
        ],
        "keywords": ["car", "crash", "damage", "physics", "vehicle"]
    },
    {
        "batch_num": 2,
        "internal_theme": "POLICE_CHASE_5_STAR",
        "target_seed_audience": "High-octane pursuit fans, police evasion, fast-paced action gamers",
        "editorial_angle": "High-energy cut cadence (every 2.2s), siren audio enhancement, drift accents",
        "default_bgm": "ncs_warriyo_mortals.mp3",
        "title_templates": [
            "The police AI in GTA 6 doesn't play around 🚓",
            "Escaping a 5-star wanted level in GTA 6 🔥",
            "GTA 6 cops are actually terrifying 💀",
            "The smartest police escape in GTA 6 history 🤯",
            "Surviving 5 stars in Vice City at 1 HP 🔥"
        ],
        "keywords": ["police", "cops", "pursuit", "chase", "wanted"]
    },
    {
        "batch_num": 3,
        "internal_theme": "WATER_AND_STORM_GRAPHICS",
        "target_seed_audience": "Next-gen tech enthusiasts, Unreal Engine fans, graphical fidelity viewers",
        "editorial_angle": "Showcase pacing (3.5s cadence), environmental audio clarity, color vibrancy pop",
        "default_bgm": "ncs_lost_sky_where_we_started.mp3",
        "title_templates": [
            "Look at how the water moves in GTA 6 🤯",
            "GTA 6 graphics in a hurricane are insane 🌊",
            "Rockstar spent 10 years on this water physics 💀",
            "The lighting in GTA 6 Vice City is unmatched ✨",
            "GTA 6 looks better than real life right now 😱"
        ],
        "keywords": ["water", "graphics", "storm", "hurricane", "lighting"]
    },
    {
        "batch_num": 4,
        "internal_theme": "STREAMER_HIGH_ENERGY_CHAOS",
        "target_seed_audience": "Gen-Z stream clip community, IShowSpeed / Kai Cenat viewers, meme lovers",
        "editorial_angle": "Rapid cuts on screams (1.5s cadence), facecam dynamic punch-ins, audio limiter",
        "default_bgm": "ncs_different_heaven_my_heart.mp3",
        "title_templates": [
            "Speed lost his mind playing GTA 6 💀",
            "He was not ready for GTA 6 Vice City 😭",
            "Speed broke the GTA 6 map in 5 seconds 💀",
            "Bro could not believe what just happened in GTA 6 🤯",
            "His reaction to GTA 6 Vice City is priceless 😂"
        ],
        "keywords": ["speed", "reaction", "unbelievable", "crazy", "scream"]
    },
    {
        "batch_num": 5,
        "internal_theme": "LUCIA_AND_JASON_NARRATIVE",
        "target_seed_audience": "GTA storyline fans, character dynamic admirers, Bonnie & Clyde crime fans",
        "editorial_angle": "Dialogue focus, narrative tension ramp, kinetic text highlighting on character names",
        "default_bgm": "ncs_janji_heroes_tonight.mp3",
        "title_templates": [
            "Lucia and Jason taking over Vice City 🔥",
            "Lucia does not play around in GTA 6 😳",
            "The chemistry between Jason and Lucia is insane 🔫",
            "GTA 6 story moments hit completely different ✨",
            "When Lucia takes the wheel in GTA 6 💀"
        ],
        "keywords": ["lucia", "jason", "story", "vice", "heist"]
    },
    {
        "batch_num": 6,
        "internal_theme": "UNDERGROUND_MUD_AND_NIGHTLIFE",
        "target_seed_audience": "Florida culture voyeurs, mudding fans, sandbox realism observers",
        "editorial_angle": "Heavy bass groove, mud particle focus, quick cuts on crowd reactions",
        "default_bgm": "ncs_culture_code_make_me_move.mp3",
        "title_templates": [
            "GTA 6 mud club physics look crazy 🚜💨",
            "Vice City nightlife in GTA 6 is wild 🌃",
            "Rockstar nailed the Florida mud culture 💀",
            "The crowd detail in GTA 6 is unbelievable 😳",
            "You won't believe what happens at this GTA 6 club 💀"
        ],
        "keywords": ["mud", "club", "nightlife", "crowd", "florida"]
    },
    {
        "batch_num": 7,
        "internal_theme": "SUPERCAR_DRIFT_AND_SPEED",
        "target_seed_audience": "Car culture, JDM & exotic supercar lovers, drift stunt fans",
        "editorial_angle": "Engine audio boost, cornering speed-ramps, neon border sync",
        "default_bgm": "ncs_disfigure_blank.mp3",
        "title_templates": [
            "This hypercar drift in GTA 6 was too clean 🏎️💨",
            "Top speed on the Vice City highway in GTA 6 🔥",
            "The exhaust notes in GTA 6 sound so real 🎵",
            "Drifting through Vice City traffic in GTA 6 🤯",
            "The fastest car in GTA 6 tested to the limit ⚡"
        ],
        "keywords": ["supercar", "drift", "speed", "highway", "engine"]
    },
    {
        "batch_num": 8,
        "internal_theme": "NPC_AI_AND_RAGDOLL_FAILS",
        "target_seed_audience": "Funny gaming fails fans, NPC interaction enthusiasts, ragdoll comedy",
        "editorial_angle": "Funny beat drops, slow-motion facial expressions, comedic pause cuts",
        "default_bgm": "ncs_invincible.mp3",
        "title_templates": [
            "GTA 6 NPC AI is already out of control 😂",
            "He picked a fight with the wrong NPC in GTA 6 💀",
            "When you bump into an NPC in Vice City 😭",
            "The funniest ragdoll fail in GTA 6 so far 💀",
            "GTA 6 pedestrians have zero chill 😂"
        ],
        "keywords": ["npc", "ragdoll", "fight", "fail", "hilarious"]
    },
    {
        "batch_num": 9,
        "internal_theme": "XQC_RAGE_AND_CHAOS",
        "target_seed_audience": "Twitch stream highlight fans, xQc viewers, chaotic comedy crowd",
        "editorial_angle": "Vocal pitch tracking, desk slam cut-aways, dynamic zoom",
        "default_bgm": "ncs_sky_high.mp3",
        "title_templates": [
            "xQc rage in GTA 6 is peak comedy 😭💀",
            "Chat told him not to drive this car in GTA 6 💀",
            "xQc totaled his GTA 6 supercar in 10 seconds 🚗💥",
            "The moment xQc realized GTA 6 has realistic gravity 💀",
            "xQc cannot handle the GTA 6 traffic 😭"
        ],
        "keywords": ["xqc", "rage", "stream", "chat", "accident"]
    },
    {
        "batch_num": 10,
        "internal_theme": "SECRET_EASTER_EGGS_AND_LORE",
        "target_seed_audience": "GTA lore detectives, secret hunters, trivia & detail nerds",
        "editorial_angle": "Curiosity gap pacing, red neon accent pops, question-first titling",
        "default_bgm": "ncs_on_and_on.mp3",
        "title_templates": [
            "5 insane details you missed in GTA 6 🔍",
            "Rockstar hid this secret in Vice City 🤫",
            "Did anyone else notice this in GTA 6? 🤯",
            "The dark secret hidden in GTA 6 Leonida 💀",
            "Only 1% of players spotted this in GTA 6 😳"
        ],
        "keywords": ["secret", "details", "easter egg", "hidden", "lore"]
    },
    {
        "batch_num": 11,
        "internal_theme": "COMBAT_AND_GUNPLAY_FEEL",
        "target_seed_audience": "Shooter fans, weapon mechanics enthusiasts, tactical action viewers",
        "editorial_angle": "Muzzle flash sync cuts, bass impact punch-in, combat sound clarity",
        "default_bgm": "ncs_unknown_brain_superhero.mp3",
        "title_templates": [
            "The gun recoil in GTA 6 feels too real 🔫💥",
            "GTA 6 combat mechanics are completely revamped 🔥",
            "Reload animations in GTA 6 look like real life 🤯",
            "Taking down a whole gang in GTA 6 Vice City 💀",
            "The most intense shootout in GTA 6 yet 🔫"
        ],
        "keywords": ["gun", "combat", "shootout", "weapons", "recoil"]
    },
    {
        "batch_num": 12,
        "internal_theme": "EVERGLADES_WILDLIFE_AND_GATORS",
        "target_seed_audience": "Nature & wildlife admirers, Florida swamp enthusiasts, open-world detail fans",
        "editorial_angle": "Environmental tension build-up, sudden snap cut, water splash boost",
        "default_bgm": "ncs_sidewalks_and_skeletons_crawlspace.mp3",
        "title_templates": [
            "Alligator attacks in GTA 6 are genuinely scary 🐊",
            "Exploring the GTA 6 Everglades at night 💀",
            "Do not jump in the swamp in GTA 6 😳",
            "The wildlife AI in GTA 6 is unmatched 🦆🐊",
            "He tried to pet an alligator in GTA 6 💀"
        ],
        "keywords": ["alligator", "swamp", "wildlife", "everglades", "gator"]
    },
    {
        "batch_num": 13,
        "internal_theme": "BMX_AND_PARKOUR_STUNTS",
        "target_seed_audience": "Extreme sports gamers, skate/BMX lovers, stunt montage audience",
        "editorial_angle": "Rhythmic beat drops, height aerial tracking, mid-air freeze zoom",
        "default_bgm": "ncs_narvent_axstin_cloud_9.mp3",
        "title_templates": [
            "The bicycle physics in GTA 6 are actually crazy 🚲",
            "Doing insane roof stunts in GTA 6 Vice City 🛹",
            "He landed this impossible jump in GTA 6 🤯",
            "GTA 6 parkour and ragdoll moments 🔥",
            "When you take a BMX up the Vice City tower 💀"
        ],
        "keywords": ["stunt", "bmx", "jump", "trick", "bicycle"]
    },
    {
        "batch_num": 14,
        "internal_theme": "SYNTHWAVE_NEON_CINEMATIC",
        "target_seed_audience": "Aesthetic lovers, lofi/synthwave chill gamers, retro 80s Vice City fans",
        "editorial_angle": "Smooth 3.5s pacing, neon cyan/magenta grading, ambient road audio",
        "default_bgm": "ncs_julius_dreisig_invisible.mp3",
        "title_templates": [
            "Cruising through GTA 6 Vice City at 2 AM ✨",
            "The sunset aesthetic in GTA 6 is pure art 🌅",
            "Why GTA 6 Vice City feels so nostalgic 🌴✨",
            "Driving down Ocean Drive in GTA 6 🌃",
            "GTA 6 midnight vibes hit different 🎵"
        ],
        "keywords": ["aesthetic", "sunset", "neon", "drive", "vibes"]
    },
    {
        "batch_num": 15,
        "internal_theme": "CONVENIENCE_STORE_HEISTS",
        "target_seed_audience": "Roleplay fans, GTA RP community, heist drama viewers",
        "editorial_angle": "Clock ticking tension, quick vault over counter, siren climax drop",
        "default_bgm": "ncs_jim_yosef_firefly.mp3",
        "title_templates": [
            "Robbing a gas station in GTA 6 went completely wrong 😭",
            "The clerk in GTA 6 pulled out a shotgun 😳💀",
            "Fastest convenience store heist in GTA 6 🔥",
            "When a routine robbery turns into 4 stars in GTA 6 🚓",
            "GTA 6 robbery mechanics are next level 💰"
        ],
        "keywords": ["robbery", "store", "heist", "clerk", "cash"]
    },
    {
        "batch_num": 16,
        "internal_theme": "KAI_CENAT_LIVE_MOMENTS",
        "target_seed_audience": "Kai Cenat community, AMP fans, stream comedy crowd",
        "editorial_angle": "Facial expressions cut, chat reaction framing, vocal emphasis",
        "default_bgm": "ncs_tonytonychopper999_feel_the_rush.mp3",
        "title_templates": [
            "Kai Cenat saw the GTA 6 graphics and lost it 😭",
            "Kai Cenat tries driving in GTA 6 Vice City 🚗💀",
            "When Kai realizes how big the GTA 6 map is 🤯",
            "Kai Cenat meets his first GTA 6 alligator 🐊💀",
            "Kai Cenat's honest reaction to GTA 6 gameplay 😂"
        ],
        "keywords": ["kai", "cenat", "amp", "map", "react"]
    },
    {
        "batch_num": 17,
        "internal_theme": "SLOW_MOTION_DEFORMATION",
        "target_seed_audience": "Detail-oriented tech viewers, slow-mo fans, engineering nerds",
        "editorial_angle": "0.5x speed ramps, crisp glass-shatter audio, frame-by-frame zoom",
        "default_bgm": "ncs_vinter_wherever_you_go.mp3",
        "title_templates": [
            "GTA 6 vehicle damage in slow motion is mindblowing 🤯",
            "Watching tire physics in GTA 6 at 10% speed 🏎️",
            "Glass shattering mechanics in GTA 6 slowed down ✨",
            "How metal crumbles in GTA 6 crashes 🚗💥",
            "You never noticed this collision detail in GTA 6 🔍"
        ],
        "keywords": ["slowmo", "deformation", "glass", "crumble", "metal"]
    },
    {
        "batch_num": 18,
        "internal_theme": "OFFROAD_MUDDING_AND_4X4",
        "target_seed_audience": "4x4 truck fans, off-road enthusiasts, mudding culture",
        "editorial_angle": "Suspension flex focus, muddy rooster-tail splashes, revving audio",
        "default_bgm": "ncs_sace_caramel.mp3",
        "title_templates": [
            "Taking a lifted truck into the GTA 6 mud pits 🚜💨",
            "The suspension physics on 4x4 trucks in GTA 6 🤯",
            "Can this offroad truck survive deep water in GTA 6? 🌊",
            "GTA 6 mudding with the crew looks insane 🔥",
            "Testing 4x4 trucks against GTA 6 terrain ⛰️"
        ],
        "keywords": ["truck", "offroad", "4x4", "lifted", "suspension"]
    },
    {
        "batch_num": 19,
        "internal_theme": "AERIAL_AND_HELICOPTER_VIEWS",
        "target_seed_audience": "Flight enthusiasts, aerial landscape lovers, scale comparison viewers",
        "editorial_angle": "High camera angle top 60%, rotor blade audio ducking, panoramic sweep",
        "default_bgm": "ncs_whvtheduck_underskin.mp3",
        "title_templates": [
            "Flying over Vice City at sunset in GTA 6 🚁🌅",
            "The sheer scale of the GTA 6 map from a helicopter 🤯",
            "Low-altitude flight through Vice City skyscrapers 🌆",
            "GTA 6 draw distance from 10,000 feet up ✨",
            "Helicopter physics in GTA 6 are crazy realistic 🚁"
        ],
        "keywords": ["fly", "helicopter", "skyline", "aerial", "clouds"]
    },
    {
        "batch_num": 20,
        "internal_theme": "IMPOSSIBLE_CLUTCHES_AND_1V4",
        "target_seed_audience": "Competitive gamers, clutch clips, high-skill montage viewers",
        "editorial_angle": "Fast cut acceleration into climax drop, heartbeat audio effect, victory cheer",
        "default_bgm": "ncs_lost_sky_where_we_started.mp3",
        "title_templates": [
            "The most impossible 1v4 clutch in GTA 6 🔥",
            "He had 1 HP left and pulled THIS off 🤯",
            "Top 1% movement skills in GTA 6 Vice City ⚡",
            "Nobody believed he could survive this in GTA 6 💀",
            "The cleanest clutch in GTA 6 history 🏆"
        ],
        "keywords": ["clutch", "1v4", "skill", "impossible", "survive"]
    }
]


def build_manifest():
    print("Building 20-Batch A/B Testing Manifest...", flush=True)

    # Start scheduling at 14:00 IST today (2026-11-21 14:00:00)
    # Spaced every 1 hour (20 batches across 20 hours)
    base_time = datetime(2026, 11, 21, 14, 0, 0)
    batches = []
    total_videos = 0

    # Load candidate raw/viral videos to assign
    with open(STORAGE_DIR / "candidates_pure_gta6.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)

    # Pool of 100+ raw videos
    cand_pool = candidates[:100]

    for b_idx, prof in enumerate(AUDIENCE_PROFILES):
        batch_num = prof["batch_num"]
        scheduled_dt = base_time + timedelta(hours=1 * b_idx)
        scheduled_iso = scheduled_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        scheduled_ist_str = scheduled_dt.strftime("%d-%b-%Y %I:%M %p IST")

        batch_videos = []
        for v_idx in range(5):
            global_vid_num = b_idx * 5 + v_idx + 1
            cand = cand_pool[global_vid_num - 1] if global_vid_num - 1 < len(cand_pool) else cand_pool[0]
            vid_id = cand["id"]
            title = prof["title_templates"][v_idx]
            
            # Natural description (no mention of batch or seed audience)
            description = (
                f"{title}\n\n"
                "Captured in GTA 6 Vice City. Rendered in 2K 1440x2560 vertical layout with NeuralClips.\n\n"
                "#GTA6 #Shorts #Gaming #GTA6Gameplay #ViceCity"
            )

            clip_record = {
                "video_number": global_vid_num,
                "clip_id": f"clip_batch_{batch_num:02d}_{v_idx+1:02d}_{vid_id}",
                "source_video_id": vid_id,
                "source_file": str(STORAGE_DIR / "viral_100_clips" / f"{vid_id}.mp4"),
                "rendered_file": str(STORAGE_DIR / "cooked_100_batches" / f"batch_{batch_num:02d}" / f"clip_{global_vid_num:03d}_{vid_id}.mp4"),
                "title": title,
                "description": description,
                "duration_seconds": 35.0,
                "bgm_track": prof["default_bgm"],
                "status": "QUEUED"
            }
            batch_videos.append(clip_record)
            total_videos += 1

        batch_entry = {
            "batch_number": batch_num,
            "internal_theme": prof["internal_theme"],
            "target_seed_audience": prof["target_seed_audience"],
            "editorial_hypothesis": prof["editorial_angle"],
            "scheduled_release_time_iso": scheduled_iso,
            "scheduled_release_time_ist": scheduled_ist_str,
            "status": "SCHEDULED",
            "videos": batch_videos
        }
        batches.append(batch_entry)

    manifest_data = {
        "manifest_version": "2.0-VIRAL-BATCH-EXPERIMENT",
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

    print(f"Successfully generated {len(batches)} unique batches ({total_videos} total videos).")
    print(f"Manifest written to: {MANIFEST_FILE}")


if __name__ == "__main__":
    build_manifest()

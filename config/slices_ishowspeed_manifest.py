"""IShowSpeed 24-Shorts Wave Manifest.

Configures 24 high-intensity 1.5-minute (90-second) clips extracted from IShowSpeed's GTA stream,
divided into 4 scheduled waves spaced 30 minutes apart (at least 6 videos per wave).
"""

from pathlib import Path

SOURCE_STREAM = r"d:\vidclip\storage\review_cuts\source_speed_stream_36min.mp4"
OUTPUT_DIR = r"d:\vidclip\storage\batch_ishowspeed"
THUMB_DIR = r"d:\vidclip\storage\thumbnails_speed"

WAVES = [
    {
        "wave_id": 1,
        "wave_name": "Wave 1 - Heists & Supercar Police Pursuits",
        "publish_at_ist": "2026-11-23 13:30:00 IST",
        "publish_at_utc": "2026-11-23T08:00:00.000Z",
        "videos": [
            {
                "id": "speed_wave1_01",
                "start_sec": 0.0,
                "duration": 90.0,
                "hook_title": "SPEED FIRST GTA 6 COP CHASE 🚓💀",
                "title": "Speed's First Cop Chase in GTA 6 Went Horribly Wrong 😭💀",
                "description": "Speed trying to outrun Vice City police for 90 seconds straight!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 funny moments", "Vice City"]
            },
            {
                "id": "speed_wave1_02",
                "start_sec": 90.0,
                "duration": 90.0,
                "hook_title": "SPEED HYPERCAR CRASH IN VICE CITY 🏎️💥",
                "title": "Speed Crashed a $3M Hypercar at 250 MPH in GTA 6 💀🏎️",
                "description": "Speed tests top speed on the Vice City freeway and this happens!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 hypercar", "Vice City"]
            },
            {
                "id": "speed_wave1_03",
                "start_sec": 180.0,
                "duration": 90.0,
                "hook_title": "SPEED VS VICE CITY POLICE SWAT 🔫😱",
                "title": "Speed Surrounded by 50 SWAT Officers in GTA 6 😱💀",
                "description": "Speed trapped in an alleyway with maximum wanted level!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 SWAT", "Vice City"]
            },
            {
                "id": "speed_wave1_04",
                "start_sec": 270.0,
                "duration": 90.0,
                "hook_title": "SPEED FOUND SECRET WEAPON IN GTA 6 💣🔥",
                "title": "Speed Found the Most Overpowered Weapon in GTA 6 🔥💣",
                "description": "Speed testing the secret rocket launcher in Vice City!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 secret weapon", "Vice City"]
            },
            {
                "id": "speed_wave1_05",
                "start_sec": 360.0,
                "duration": 90.0,
                "hook_title": "SPEED ACCIDENTALLY JUMPS OFF BRIDGE 🌉😭",
                "title": "Speed Accidentally Launched His Car Off the Bridge 😭🚗",
                "description": "Speed tried to make an impossible jump and instantly regretted it!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 stunt jump", "Vice City"]
            },
            {
                "id": "speed_wave1_06",
                "start_sec": 450.0,
                "duration": 90.0,
                "hook_title": "SPEED ESCAPES 5-STAR WANTED LEVEL 🔥🏃",
                "title": "When Speed Escaped 5 Stars at 1 HP in GTA 6 💀🔥",
                "description": "One bullet away from wasted and Speed pulls off the greatest escape!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 escape", "Vice City"]
            }
        ]
    },
    {
        "wave_id": 2,
        "wave_name": "Wave 2 - Underworld & Military Stunts",
        "publish_at_ist": "2026-11-23 14:00:00 IST",
        "publish_at_utc": "2026-11-23T08:30:00.000Z",
        "videos": [
            {
                "id": "speed_wave2_01",
                "start_sec": 540.0,
                "duration": 90.0,
                "hook_title": "SPEED FINDS SECRET UNDERGROUND CLUB 😳🕺",
                "title": "Speed Discovered the Hidden VIP Club in GTA 6 Vice City 😳🕺",
                "description": "Speed sneaking into the most exclusive club in Vice City!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 easter egg", "Vice City"]
            },
            {
                "id": "speed_wave2_02",
                "start_sec": 630.0,
                "duration": 90.0,
                "hook_title": "SPEED STEALS A MILITARY TANK 🪖💥",
                "title": "Speed Stole a Military Tank and Caused Pure Chaos 💀🪖",
                "description": "Speed breaks into the military base and blasts everything in sight!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 tank", "Vice City"]
            },
            {
                "id": "speed_wave2_03",
                "start_sec": 720.0,
                "duration": 90.0,
                "hook_title": "SPEED TRIES TO FLY A HELICOPTER 🚁💀",
                "title": "Speed Flying a Police Helicopter in a Category 5 Storm 🚁🌪️",
                "description": "Speed vs extreme weather physics in GTA 6!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 helicopter", "Vice City"]
            },
            {
                "id": "speed_wave2_04",
                "start_sec": 810.0,
                "duration": 90.0,
                "hook_title": "SPEED RAGES AT GTA 6 PHYSICS 😭💢",
                "title": "Speed Loses His Mind After Getting Hit by a Train 💀🚂",
                "description": "Speed tested train physics in GTA 6 and had the ultimate crash!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 rage", "Vice City"]
            },
            {
                "id": "speed_wave2_05",
                "start_sec": 900.0,
                "duration": 90.0,
                "hook_title": "SPEED FASTEST MOTORCYCLE STUNT 🏍️💨",
                "title": "Speed Hit 200 MPH on a Superbike Through Downtown Traffic 🏍️🔥",
                "description": "Speed lane-splitting at insane speed across Vice City!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 motorcycle", "Vice City"]
            },
            {
                "id": "speed_wave2_06",
                "start_sec": 990.0,
                "duration": 90.0,
                "hook_title": "SPEED MEETS LUCIA IN VICE CITY 😂❤️",
                "title": "Speed's Honest Reaction to Meeting Lucia in GTA 6 😂❤️",
                "description": "Speed cannot handle the realism of the NPC interactions in GTA 6!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "Lucia GTA 6", "Vice City"]
            }
        ]
    },
    {
        "wave_id": 3,
        "wave_name": "Wave 3 - High Stakes & Military Rampages",
        "publish_at_ist": "2026-11-23 14:30:00 IST",
        "publish_at_utc": "2026-11-23T09:00:00.000Z",
        "videos": [
            {
                "id": "speed_wave3_01",
                "start_sec": 1080.0,
                "duration": 90.0,
                "hook_title": "SPEED ATTEMPTS FLEECA BANK HEIST 🏦💰",
                "title": "Speed Tried to Rob the Biggest Bank in Vice City Solo 💰🏦",
                "description": "The alarm goes off and 20 squad cars instantly arrive on Speed!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 heist", "Vice City"]
            },
            {
                "id": "speed_wave3_02",
                "start_sec": 1170.0,
                "duration": 90.0,
                "hook_title": "SPEED VS 100 VICE CITY COPS 🚓💀",
                "title": "Speed Held Off the ENTIRE Vice City Police Force 💀🚓",
                "description": "Speed armed with a minigun fighting waves of law enforcement!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 cops", "Vice City"]
            },
            {
                "id": "speed_wave3_03",
                "start_sec": 1260.0,
                "duration": 90.0,
                "hook_title": "SPEED SURVIVES PLANE CRASH ✈️💥",
                "title": "Speed Crashed a Commercial Jet into Ocean Drive and LIVED 🤯✈️",
                "description": "Speed tests aerodynamic damage models in the heart of Vice City!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 plane crash", "Vice City"]
            },
            {
                "id": "speed_wave3_04",
                "start_sec": 1350.0,
                "duration": 90.0,
                "hook_title": "SPEED FINDS GOLDEN SUPERCAR 🏎️✨",
                "title": "Speed Discovered the Secret 1-of-1 Gold Supercar in GTA 6 ✨🏎️",
                "description": "Speed customized the rarest exotic vehicle in the entire game!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 supercar", "Vice City"]
            },
            {
                "id": "speed_wave3_05",
                "start_sec": 1440.0,
                "duration": 90.0,
                "hook_title": "SPEED LOSES HIS CAR IN THE WATER 🌊🚗",
                "title": "Speed Drove His $2M Supercar Directly into the Ocean 😭🌊",
                "description": "Speed misjudged the harbor turn and submerged the hypercar!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 funny moments", "Vice City"]
            },
            {
                "id": "speed_wave3_06",
                "start_sec": 1530.0,
                "duration": 90.0,
                "hook_title": "SPEED UNLOCKS 6-STAR MILITARY BASE 🪖🚨",
                "title": "Speed Activated 6-Star Wanted Level at Fort Zancudo 🚨🪖",
                "description": "Tanks, jets, and attack helicopters spawn to hunt down Speed!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 6-star", "Vice City"]
            }
        ]
    },
    {
        "wave_id": 4,
        "wave_name": "Wave 4 - Skyscraper Jumps & Grand Finale",
        "publish_at_ist": "2026-11-23 15:00:00 IST",
        "publish_at_utc": "2026-11-23T09:30:00.000Z",
        "videos": [
            {
                "id": "speed_wave4_01",
                "start_sec": 1620.0,
                "duration": 90.0,
                "hook_title": "SPEED JUMPS SUPERCAR OFF SKYSCRAPER 🏢🏎️",
                "title": "Speed Jumped a Supercar off the Tallest Tower in GTA 6 🏢💀",
                "description": "Parachuting out of a falling hypercar over downtown Vice City!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 skyscraper jump", "Vice City"]
            },
            {
                "id": "speed_wave4_02",
                "start_sec": 1710.0,
                "duration": 90.0,
                "hook_title": "SPEED CONFRONTS THE MAFIA BOSS 🔫😨",
                "title": "Speed Infiltrated the Vice City Cartel Mansion 😨🔫",
                "description": "Speed tries stealth gameplay and immediately alerts 30 guards!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 mafia", "Vice City"]
            },
            {
                "id": "speed_wave4_03",
                "start_sec": 1800.0,
                "duration": 90.0,
                "hook_title": "SPEED SPEEDRUNS VICE CITY HIGHWAY 🛣️⚡",
                "title": "Speed's Record-Breaking Highway Run from North to South ⚡🏎️",
                "description": "Full throttle across the entire Leonida map without lifting off the gas!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 speedrun", "Vice City"]
            },
            {
                "id": "speed_wave4_04",
                "start_sec": 1890.0,
                "duration": 90.0,
                "hook_title": "SPEED DISCOVERS SECRET MILITARY BUNKER 🤫🛡️",
                "title": "Speed Found an Underground Experimental Laboratory in GTA 6 🤫🧪",
                "description": "Hidden elevator deep beneath the Everglades swamp uncovered by Speed!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 secret bunker", "Vice City"]
            },
            {
                "id": "speed_wave4_05",
                "start_sec": 1980.0,
                "duration": 90.0,
                "hook_title": "SPEED HIGHEST BOUNTY IN GTA 6 💰🚨",
                "title": "Speed Had a $1,000,000 Bounty on His Head in GTA 6 💀💰",
                "description": "Every player and bounty hunter in the lobby hunting Speed for 90 seconds!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 bounty", "Vice City"]
            },
            {
                "id": "speed_wave4_06",
                "start_sec": 2070.0,
                "duration": 90.0,
                "hook_title": "SPEED FINAL ESCAPE FROM VICE CITY 🔥🛥️",
                "title": "Speed's Insane Speedboat Escape into International Waters 🛥️🔥",
                "description": "Coast guard gunboats chasing Speed past the boundary in the grand finale!\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline",
                "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 speedboat", "Vice City"]
            }
        ]
    }
]

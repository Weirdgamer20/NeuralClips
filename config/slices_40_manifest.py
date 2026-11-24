"""Defines the 40 high-retention 2K clip slices across verified master sources.
"""

# Each clip is 25 to 30 seconds
# Quality: 1080x1920 @ 60 FPS (or 30 FPS), Lanczos, setsar=1, audio synced

SLICES_CONFIG = [
    # --- 10 CUTS: 1440p Tank 6-Star Rampage (storage/review_cuts/tank_6star_1440p.webm) ---
    {"id": "tank_01", "src": "tank_6star_1440p.webm", "start": 30, "dur": 28, "title": "GTA 6 TANK Crushes Entire Police Convoy 💀🪖 #Shorts", "hook": "CONVOY CRUSH! 💥", "type": "1440p"},
    {"id": "tank_02", "src": "tank_6star_1440p.webm", "start": 75, "dur": 28, "title": "Blowing Up Police Helicopters with a Tank in GTA 6 💀🚁 #Shorts", "hook": "CHOPPER BLOWOUT! 🔥", "type": "1440p"},
    {"id": "tank_03", "src": "tank_6star_1440p.webm", "start": 120, "dur": 28, "title": "When a SWAT Tank Meets GTA 6 Vice City Police 💀 #Shorts", "hook": "SWAT BARRICADE! 🚨", "type": "1440p"},
    {"id": "tank_04", "src": "tank_6star_1440p.webm", "start": 165, "dur": 28, "title": "GTA 6 6-Star Wanted Tank Rampage on Highway 💀 #Shorts", "hook": "HIGHWAY RAMPAGE! 🚗", "type": "1440p"},
    {"id": "tank_05", "src": "tank_6star_1440p.webm", "start": 210, "dur": 28, "title": "Can Any Vehicle Stop the GTA 6 Tank?! 😱 #Shorts", "hook": "UNSTOPPABLE! 🪖", "type": "1440p"},
    {"id": "tank_06", "src": "tank_6star_1440p.webm", "start": 255, "dur": 28, "title": "Extreme Police Chain Reaction Explosion in GTA 6 💥 #Shorts", "hook": "CHAIN EXPLOSION! 💣", "type": "1440p"},
    {"id": "tank_07", "src": "tank_6star_1440p.webm", "start": 300, "dur": 28, "title": "Tank vs 20 Police Cruisers in GTA 6 Vice City 💀 #Shorts", "hook": "1 VS 20 COPS! 🚔", "type": "1440p"},
    {"id": "tank_08", "src": "tank_6star_1440p.webm", "start": 380, "dur": 28, "title": "GTA 6 Military Response at 6 Stars is BRUTAL 💀 #Shorts", "hook": "MILITARY STRIKE! ⚡", "type": "1440p"},
    {"id": "tank_09", "src": "tank_6star_1440p.webm", "start": 430, "dur": 28, "title": "Destroying the Vice City Bridge Roadblock in GTA 6 💀 #Shorts", "hook": "BRIDGE BREAKOUT! 🌉", "type": "1440p"},
    {"id": "tank_10", "src": "tank_6star_1440p.webm", "start": 480, "dur": 28, "title": "Last Stand Against 6-Star Police in GTA 6 💀 #Shorts", "hook": "LAST STAND! 💀", "type": "1440p"},

    # --- 10 CUTS: 1440p Supercar Pursuit (storage/review_cuts/full_4k_supercar_chase.mp4.webm) ---
    {"id": "supercar_01", "src": "full_4k_supercar_chase.mp4.webm", "start": 15, "dur": 28, "title": "180 MPH Highway Run in GTA 6 Supercar 🏎️💨 #Shorts", "hook": "180 MPH RUN! 🏁", "type": "1440p"},
    {"id": "supercar_02", "src": "full_4k_supercar_chase.mp4.webm", "start": 80, "dur": 28, "title": "Insane Cop Dodge at 160 MPH in GTA 6 💀 #Shorts", "hook": "COP DODGE! 🚨", "type": "1440p"},
    {"id": "supercar_03", "src": "full_4k_supercar_chase.mp4.webm", "start": 145, "dur": 28, "title": "Near-Miss Traffic Weave on Vice City Interstate 😱 #Shorts", "hook": "NEAR-MISS WEAVE! 🚗", "type": "1440p"},
    {"id": "supercar_04", "src": "full_4k_supercar_chase.mp4.webm", "start": 190, "dur": 28, "title": "Tunnel Drift at 150 MPH in GTA 6 Supercar 💨 #Shorts", "hook": "TUNNEL DRIFT! 🏎️", "type": "1440p"},
    {"id": "supercar_05", "src": "full_4k_supercar_chase.mp4.webm", "start": 235, "dur": 28, "title": "When Police Try to PIT Maneuver a GTA 6 Supercar 💀 #Shorts", "hook": "PIT MANEUVER FAIL! 💥", "type": "1440p"},
    {"id": "supercar_06", "src": "full_4k_supercar_chase.mp4.webm", "start": 280, "dur": 28, "title": "High Speed Off-Road Shortcut in GTA 6 🚗💨 #Shorts", "hook": "OFF-ROAD DIRT! 🌾", "type": "1440p"},
    {"id": "supercar_07", "src": "full_4k_supercar_chase.mp4.webm", "start": 325, "dur": 28, "title": "Vice City Beach Boulevard Pursuit at 170 MPH 🌴 #Shorts", "hook": "BEACH PURSUIT! 🌴", "type": "1440p"},
    {"id": "supercar_08", "src": "full_4k_supercar_chase.mp4.webm", "start": 370, "dur": 28, "title": "Threading the Needle Between Two Police Cruisers 🎯 #Shorts", "hook": "PERFECT GAP! 🎯", "type": "1440p"},
    {"id": "supercar_09", "src": "full_4k_supercar_chase.mp4.webm", "start": 440, "dur": 28, "title": "Fastest Escape Route in GTA 6 Vice City 🏎️💨 #Shorts", "hook": "FASTEST ESCAPE! 💨", "type": "1440p"},
    {"id": "supercar_10", "src": "full_4k_supercar_chase.mp4.webm", "start": 500, "dur": 28, "title": "Final 5-Star Police Evasion in GTA 6 💀🚨 #Shorts", "hook": "5-STAR EVADED! 🚨", "type": "1440p"},

    # --- 10 CUTS: Red Arcade 1080p60 Epic Fails & Stunts (storage/review_cuts/redarcade_gta6_fails.mp4.webm) ---
    {"id": "fails_01", "src": "redarcade_gta6_fails.mp4.webm", "start": 20, "dur": 28, "title": "When GTA 6 Physics COMPLETELY BREAK 💀🚀 #Shorts", "hook": "PHYSICS BROKEN! 🚀", "type": "1080p"},
    {"id": "fails_02", "src": "redarcade_gta6_fails.mp4.webm", "start": 70, "dur": 28, "title": "Funniest Car Flip into a Swimming Pool in GTA 6 😂🏊 #Shorts", "hook": "POOL CRASH! 💦", "type": "1080p"},
    {"id": "fails_03", "src": "redarcade_gta6_fails.mp4.webm", "start": 130, "dur": 28, "title": "Fastest Motorcycle Stunt Gone Horribly Wrong in GTA 6 💀 #Shorts", "hook": "BIKE WIPEOUT! 🏍️", "type": "1080p"},
    {"id": "fails_04", "src": "redarcade_gta6_fails.mp4.webm", "start": 190, "dur": 28, "title": "Helicopter Blades vs Parachute in GTA 6 😱🚁 #Shorts", "hook": "BLADE STRIKE! 🚁", "type": "1080p"},
    {"id": "fails_05", "src": "redarcade_gta6_fails.mp4.webm", "start": 250, "dur": 28, "title": "Instant Karma in GTA 6 Vice City Traffic 💀🚗 #Shorts", "hook": "INSTANT KARMA! 🚗", "type": "1080p"},
    {"id": "fails_06", "src": "redarcade_gta6_fails.mp4.webm", "start": 310, "dur": 28, "title": "Train Collision Launches Truck 1000 Feet High in GTA 6 🚂 #Shorts", "hook": "TRAIN ROCKET! 🚂", "type": "1080p"},
    {"id": "fails_07", "src": "redarcade_gta6_fails.mp4.webm", "start": 370, "dur": 28, "title": "Fastest Supercar Hits Invisible Glitch in GTA 6 💀 #Shorts", "hook": "GLITCH LAUNCH! 💥", "type": "1080p"},
    {"id": "fails_08", "src": "redarcade_gta6_fails.mp4.webm", "start": 430, "dur": 28, "title": "Skydive Into Moving Convertible in GTA 6 🎯🔥 #Shorts", "hook": "PERFECT LANDING! 🎯", "type": "1080p"},
    {"id": "fails_09", "src": "redarcade_gta6_fails.mp4.webm", "start": 490, "dur": 28, "title": "Police Cruiser Flying Barrel Roll in GTA 6 🚨 #Shorts", "hook": "BARREL ROLL! 🚨", "type": "1080p"},
    {"id": "fails_10", "src": "redarcade_gta6_fails.mp4.webm", "start": 550, "dur": 28, "title": "Insane Rooftop Supercar Jump in Vice City 🏢🚗 #Shorts", "hook": "ROOFTOP JUMP! 🏢", "type": "1080p"},

    # --- 5 CUTS: CaseOh Rage & Funny Moments (storage/review_cuts/caseoh_full_crashes.mp4.mkv) ---
    {"id": "caseoh_01", "src": "caseoh_full_crashes.mp4.mkv", "start": 10, "dur": 28, "title": "CaseOh First Time Driving GTA 6 Truck (HE RAGED) 💀 #Shorts", "hook": "CASEOH RAGE! 💀", "type": "caseoh"},
    {"id": "caseoh_02", "src": "caseoh_full_crashes.mp4.mkv", "start": 60, "dur": 28, "title": "CaseOh Flying Through Windshield in GTA 6 💀🚗 #Shorts", "hook": "WINDSHIELD FLY! 🚀", "type": "caseoh"},
    {"id": "caseoh_03", "src": "caseoh_full_crashes.mp4.mkv", "start": 120, "dur": 28, "title": "CaseOh Cannot Stop Screaming in GTA 6 😂🔊 #Shorts", "hook": "SCREAMING RAGE! 🔊", "type": "caseoh"},
    {"id": "caseoh_04", "src": "caseoh_full_crashes.mp4.mkv", "start": 180, "dur": 28, "title": "CaseOh Breaks GTA 6 Vehicle Physics Instantly 💀 #Shorts", "hook": "TRUCK BREAKDOWN! 💥", "type": "caseoh"},
    {"id": "caseoh_05", "src": "caseoh_full_crashes.mp4.mkv", "start": 240, "dur": 28, "title": "CaseOh Hilarious Reaction to 5-Star Police in GTA 6 😂🚨 #Shorts", "hook": "5-STAR PANIC! 🚨", "type": "caseoh"},

    # --- 5 CUTS: Kai Cenat High-Energy Moments (storage/review_cuts/kai_cenat_funniest.mp4.webm) ---
    {"id": "kai_01", "src": "kai_cenat_funniest.mp4.webm", "start": 15, "dur": 28, "title": "Kai Cenat Funniest Moment in GTA 6 Vice City 😂🔥 #Shorts", "hook": "KAI CENAT CRAZY! 😂", "type": "1080p"},
    {"id": "kai_02", "src": "kai_cenat_funniest.mp4.webm", "start": 80, "dur": 28, "title": "Kai Cenat Stealing a Police Car in GTA 6 🚨💀 #Shorts", "hook": "COP CAR HEIST! 🚔", "type": "1080p"},
    {"id": "kai_03", "src": "kai_cenat_funniest.mp4.webm", "start": 150, "dur": 28, "title": "Kai Cenat Reactions in GTA 6 are UNHINGED 💀 #Shorts", "hook": "UNHINGED MOMENT! 😱", "type": "1080p"},
    {"id": "kai_04", "src": "kai_cenat_funniest.mp4.webm", "start": 220, "dur": 28, "title": "Kai Cenat Escapes 5 Stars on Foot in GTA 6 🏃💨 #Shorts", "hook": "ON FOOT ESCAPE! 🏃", "type": "1080p"},
    {"id": "kai_05", "src": "kai_cenat_funniest.mp4.webm", "start": 300, "dur": 28, "title": "Kai Cenat First Time Meeting Vice City Police 💀🚨 #Shorts", "hook": "VICE CITY POLICE! 🚨", "type": "1080p"},
]

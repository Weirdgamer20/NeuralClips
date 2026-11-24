"""Generates the full 24-wave (100 videos) manifest for IShowSpeed up to 1:00 AM.
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path("d:/vidclip")
MANIFEST_PY = BASE_DIR / "config" / "slices_ishowspeed_24waves_manifest.py"

VIRAL_HOOKS = [
    ("SPEED FIRST GTA 6 COP CHASE 🚓💀", "Speed's First Cop Chase in GTA 6 Went Horribly Wrong 😭💀"),
    ("SPEED HYPERCAR CRASH IN VICE CITY 🏎️💥", "Speed Crashed a $3M Hypercar at 250 MPH in GTA 6 💀🏎️"),
    ("SPEED VS VICE CITY POLICE SWAT 🔫😱", "Speed Surrounded by 50 SWAT Officers in GTA 6 😱💀"),
    ("SPEED FOUND SECRET WEAPON IN GTA 6 💣🔥", "Speed Found the Most Overpowered Weapon in GTA 6 🔥💣"),
    ("SPEED ACCIDENTALLY JUMPS OFF BRIDGE 🌉😭", "Speed Accidentally Launched His Car Off the Bridge 😭🚗"),
    ("SPEED ESCAPES 5-STAR WANTED LEVEL 🔥🏃", "When Speed Escaped 5 Stars at 1 HP in GTA 6 💀🔥"),
    ("SPEED FINDS SECRET UNDERGROUND CLUB 😳🕺", "Speed Discovered the Hidden VIP Club in GTA 6 Vice City 😳🕺"),
    ("SPEED STEALS A MILITARY TANK 🪖💥", "Speed Stole a Military Tank and Caused Pure Chaos 💀🪖"),
    ("SPEED TRIES TO FLY A HELICOPTER 🚁💀", "Speed Flying a Police Helicopter in a Category 5 Storm 🚁🌪️"),
    ("SPEED RAGES AT GTA 6 PHYSICS 😭💢", "Speed Loses His Mind After Getting Hit by a Train 💀🚂"),
    ("SPEED FASTEST MOTORCYCLE STUNT 🏍️💨", "Speed Hit 200 MPH on a Superbike Through Downtown Traffic 🏍️🔥"),
    ("SPEED MEETS LUCIA IN VICE CITY 😂❤️", "Speed's Honest Reaction to Meeting Lucia in GTA 6 😂❤️"),
    ("SPEED ATTEMPTS FLEECA BANK HEIST 🏦💰", "Speed Tried to Rob the Biggest Bank in Vice City Solo 💰🏦"),
    ("SPEED VS 100 VICE CITY COPS 🚓💀", "Speed Held Off the ENTIRE Vice City Police Force 💀🚓"),
    ("SPEED SURVIVES PLANE CRASH ✈️💥", "Speed Crashed a Commercial Jet into Ocean Drive and LIVED 🤯✈️"),
    ("SPEED FINDS GOLDEN SUPERCAR 🏎️✨", "Speed Discovered the Secret 1-of-1 Gold Supercar in GTA 6 ✨🏎️"),
    ("SPEED LOSES HIS CAR IN THE WATER 🌊🚗", "Speed Drove His $2M Supercar Directly into the Ocean 😭🌊"),
    ("SPEED UNLOCKS 6-STAR MILITARY BASE 🪖🚨", "Speed Activated 6-Star Wanted Level at Fort Zancudo 🚨🪖"),
    ("SPEED JUMPS SUPERCAR OFF SKYSCRAPER 🏢🏎️", "Speed Jumped a Supercar off the Tallest Tower in GTA 6 🏢💀"),
    ("SPEED CONFRONTS THE MAFIA BOSS 🔫😨", "Speed Infiltrated the Vice City Cartel Mansion 😨🔫"),
    ("SPEED SPEEDRUNS VICE CITY HIGHWAY 🛣️⚡", "Speed's Record-Breaking Highway Run from North to South ⚡🏎️"),
    ("SPEED DISCOVERS SECRET MILITARY BUNKER 🤫🛡️", "Speed Found an Underground Experimental Laboratory in GTA 6 🤫🧪"),
    ("SPEED HIGHEST BOUNTY IN GTA 6 💰🚨", "Speed Had a $1,000,000 Bounty on His Head in GTA 6 💀💰"),
    ("SPEED FINAL ESCAPE FROM VICE CITY 🔥🛥️", "Speed's Insane Speedboat Escape into International Waters 🛥️🔥"),
    ("SPEED TRIES TO PARK A YACHT 🛥️😂", "Speed Accidentally Beached a $10M Luxury Yacht on Ocean Beach 💀🛥️"),
    ("SPEED STEALTH MISSION GONE WRONG 🥷💥", "Speed Tries Stealth for 5 Seconds Before Explosions Start 😭💥"),
    ("SPEED TESTING CAR HYDRAULICS 🚗🔊", "Speed Discovered Lowrider Hydraulics in Vice City and Lost It 😂🔊"),
    ("SPEED ESCAPING POLICE IN A BUS 🚌💀", "Speed Hijacked a Public Transit Bus with a 4-Star Wanted Level 🚌🚓"),
    ("SPEED RACING THE FASTEST NPC 🏎️🏁", "Speed Got Gapped by an NPC in a Sports Car and Got Angry 💢🚗"),
    ("SPEED AT THE AIRPORT RUNWAY 🛩️🔥", "Speed Tried to Outrun a Boeing 747 on the Vice City Runway 🛩️💀"),
    ("SPEED TRIES SUBMARINE EXPLORATION 🌊🤿", "Speed Found a Sunken Ship in the Bermuda Triangle in GTA 6 🤿🚢"),
    ("SPEED VS ALLIGATORS IN THE SWAMP 🐊😱", "Speed Got Chased by 3 Giant Alligators in the Everglades 🐊🏃"),
    ("SPEED BUYS THE MOST EXPENSIVE HOUSE 🏡✨", "Speed Spent All His GTA 6 Money on a Mansion on Star Island 🏡💰"),
    ("SPEED DRIFTING IN THE RAIN 🌧️🏎️", "Speed Tokyo Drifting Through Flooded Vice City Streets 🌧️🚗"),
    ("SPEED ACCIDENTALLY BLOWS UP GAS STATION ⛽💥", "Speed Ran into a Gas Pump and Leveled the Entire Block 💀⛽"),
    ("SPEED PARACHUTE LANDING ON MOVING TRAIN 🪂🚂", "Speed Pulls Off the Most Impossible Stunt in GTA 6 History 🪂🔥"),
    ("SPEED TESTING ROCKET LAUNCHER ON HELIS 🚀🚁", "Speed Shooting Down Police Choppers with a Stinger Missile 🚀💥"),
    ("SPEED DRIVING ON RAILROAD TRACKS 🚂🚙", "Speed Playing Chicken with the High-Speed Freight Train 💀🚆"),
    ("SPEED TRIES THE AMUSEMENT PARK 🎡😂", "Speed Testing Rollercoaster Physics in GTA 6 Vice City 🎢😭"),
    ("SPEED FINDS HIDDEN MOUNTAIN BUNKER ⛰️🔍", "Speed Uncovering Secret Alien Coordinates in Mount Chiliad 👽🛸"),
    ("SPEED STREET RACE AT MIDNIGHT 🌙🏎️", "Speed in a 200 MPH Underground Drag Race with Pink Slips 🏁💨"),
    ("SPEED VS THE STRONGEST NPC IN VICE CITY 🥊💀", "Speed Challenged a Heavyweight NPC to a Fist Fight and Got KO'd 😭👊"),
    ("SPEED SURVIVES 100 FT CLIFF DROP 🚙🪨", "Speed Driving Off the Highest Mountain Peak and Survived 🤯🚗"),
    ("SPEED ROBBING A CONVENIENCE STORE 🏪💰", "Speed First Grocery Store Robbery Goes Completely Chaotic 😂🔫"),
    ("SPEED MOTORCYCLE ROOFTOP JUMP 🏍️🏢", "Speed Jumped Across 3 Skyscrapers on a Dirtbike 🏍️🔥"),
    ("SPEED FIGHTING CRIME AS BATMAN 🦇😂", "Speed Dressing Up as a Superhero to Stop NPC Crime 😭🦸"),
    ("SPEED TESTING SNIPER BULLET DROP 🎯🔫", "Speed Sniping from 1,000 Yards in GTA 6 Realistic Ballistics 🎯💥"),
    ("SPEED JET SKI STUNT IN HURRICANE 🌊⚡", "Speed Jumping Massive Ocean Waves During a Tropical Storm 🌊🚤"),
    ("SPEED GETTING TOWED BY POLICE 🚜🚓", "Speed Hooked a Cop Car to a Tow Truck and Drove into the Sea 😂🌊"),
    ("SPEED CRASH TEST DUMMY PHYSICS 🚗💥", "Speed Testing the New Ragdoll Physics in GTA 6 at Top Speed 💀🏃"),
    ("SPEED INFILTRATING MILITARY AIRBASE 🪖✈️", "Speed Stealing a Fighter Jet Under Heavy Anti-Air Missile Fire ✈️🚨"),
    ("SPEED DOING 360 SPINS IN TRAFFIC 🌪️🏎️", "Speed Spinning Donuts in the Middle of Downtown Intersection 🚗💨"),
    ("SPEED TESTING FIRE TRUCK CANNON 🚒💦", "Speed Blasting NPCs Across the Sidewalk with High Pressure Water 😂🌊"),
    ("SPEED TRIES TO FLY A CARGO PLANE ✈️📦", "Speed Landing a Giant Titan Cargo Plane on a Tiny Bridge 💀✈️"),
    ("SPEED RAGDOLL OFF RADIO TOWER 🗼😱", "Speed Jumping off the Tallest Broadcast Antenna in the State 🗼💀"),
    ("SPEED VS SWAT ARMORED VAN 🚐💥", "Speed Ramming Armored Swat Vehicles with a Monster Truck 🛞💥"),
    ("SPEED FINDS SECRET UNDERWATER TUNNEL 🚇🌊", "Speed Discovering Secret Smuggler Tunnel into the Port of Miami 🚇🚢"),
    ("SPEED ESCAPING ON A BICYCLE 🚲🚓", "Speed Outrunning 5 Police Cruisers on a BMX in the Alleyways 🚲😂"),
    ("SPEED RACING THE SUBWAY TRAIN 🚇💨", "Speed Racing the Underground Metro on Foot at Full Sprint 🏃⚡"),
    ("SPEED TESTING BULLETPROOF GLASS 🛡️🚗", "Speed Testing if the Armored Kuruma Can Withstand a Tank Shell 💣🚗"),
    ("SPEED ATTEMPTS CASINO HEIST 🎰💰", "Speed Infiltrates the Diamond Casino Vault in GTA 6 💰🎲"),
    ("SPEED DRIVING OFF AN AIRCRAFT CARRIER 🚢🚗", "Speed Launching a Hypercar Off the Deck of a Navy Carrier 💀🚢"),
    ("SPEED VS SPECIAL FORCES TEAM 🎖️🔫", "Speed Facing off Against Elite Military Squad with Dual Pistols 🔥🎖️"),
    ("SPEED JETPACK SECRET UNLOCKED 🚀✨", "Speed Found the Prototype Military Jetpack in the Everglades 🚀😱"),
    ("SPEED HIT BY LIGHTNING IN STORM ⚡🚗", "Speed's Vehicle Got Struck by Direct Lightning Bolt in GTA 6 ⚡💀"),
    ("SPEED TESTING FLAMETHROWER ON GANG 💥🔥", "Speed Armed with Military Flamethrower in the Turf War 🔥🔫"),
    ("SPEED ROOFTOP HELICOPTER SNIPING 🚁🎯", "Speed Sniping from the Skid of a Moving News Chopper 🎯🚁"),
    ("SPEED DRIFTING A SEMI TRUCK 🚛💨", "Speed Jackknifing an 18-Wheeler Truck Down the Coastal Highway 🚛💥"),
    ("SPEED ESCAPES PRISON ISLAND 🏝️🚨", "Speed Breaking Out of the Maximum Security Federal Penitentiary 🚨🏃"),
    ("SPEED TESTING DESTRUCTION ENGINE 🏢💣", "Speed Leveling a Multi-Story Parking Garage with Explosives 💣🏢"),
    ("SPEED SKYDIVING INTO A SUPERCAR 🪂🏎️", "Speed Landing Parachute Directly into the Driver Seat of a Moving Car 🤯🚗"),
    ("SPEED DRIVING UNDERWATER WITH OXYGEN 🌊🚙", "Speed Using the Amphibious Car to Cross the Ocean Channel 🚙🌊"),
    ("SPEED TESTING SUPERSONIC FIGHTER ✈️⚡", "Speed Breaking the Sound Barrier Low Over Vice City Skyscrapers ⚡✈️"),
    ("SPEED MEETS OLD MAN TREVOR 🧔😂", "Speed's Unbelievable Reaction to Meeting Trevor in GTA 6 😭💀"),
    ("SPEED HIGHEST AIRPORT JUMP 🛫🏎️", "Speed Launching Off the Airport Baggage Ramp Over a Plane 🛫🔥"),
    ("SPEED RUNNING FROM A 6-STAR TANK 🪖🏃", "Speed Dodging 120mm Tank Shells on Foot in Downtown Vice City 💀🪖"),
    ("SPEED FINDS GHOST SHIP AT NIGHT 👻🚢", "Speed Exploring Haunted Derelict Freighter at 3 AM in GTA 6 🚢👻"),
    ("SPEED DRIVING BLINDFOLDED 🙈🚗", "Speed Trying to Drive Across Vice City Freeway with Eyes Closed 😭🚗"),
    ("SPEED VS HELICOPTER ROTOR BLADES 🚁💀", "Speed Testing Propeller Damage Physics in the Most Insane Way 💀🚁"),
    ("SPEED RACING FORMULA 1 CAR 🏎️🏁", "Speed Testing Open-Wheel Racing at 220 MPH in Vice City Grand Prix 🏁🏎️"),
    ("SPEED SURVIVES 5-STAR WATER CANNON 🌊🚓", "Speed Trapped on the Pier Surrounded by Coast Guard Cutters 🚓🌊"),
    ("SPEED UNLOCKS SECRET GOLDEN GUN 🔫✨", "Speed Found the James Bond 007 Golden Pistol in Vice City 🕵️✨"),
    ("SPEED CRASHES INTO A WEDDING 💒😂", "Speed Losing Control of a Supercar and Crashing a Beach Wedding 😭💒"),
    ("SPEED SPEEDRUNNING MISSION IN 60S ⏱️⚡", "Speed Setting the World Record for Fastest Vice City Heist ⚡💰"),
    ("SPEED ACCIDENTALLY CALLS 911 ON HIMSELF 📞🚓", "Speed Drops His Phone and Summons 10 Police Units to His Location 😂📞"),
    ("SPEED TRIES HOVERCRAFT IN SWAMP 🚤🐊", "Speed Gliding Over Alligators and Mud on an Airboat 🚤💨"),
    ("SPEED HIGH SPEED FREEWAY PURSUIT 🛣️🚓", "Speed Weaving Through 100 Cars at 200 MPH with Spike Strips 🏎️💥"),
    ("SPEED TESTING LASER CANNON 🛸💥", "Speed Firing the Experimental Sci-Fi Railgun in Downtown Vice City ⚡🔫"),
    ("SPEED JUMPS INTO THE SUNSET 🌅🏎️", "Speed's Iconic Final Jump Across the Ocean Channel at Sunset 🌅🔥"),
    ("SPEED GRAND FINALE ESCAPE TO 1 AM 🎆🛥️", "Speed's Ultimate Midnight Escape Across the Border in GTA 6 🎆🔥"),
]

# Ensure at least 100 hooks
while len(VIRAL_HOOKS) < 100:
    VIRAL_HOOKS.append((
        f"SPEED INSANE GTA 6 MOMENT #{len(VIRAL_HOOKS)+1} 💀🔥",
        f"Speed's Craziest 90-Second GTA 6 Reaction and Escape #{len(VIRAL_HOOKS)+1} 😭💀"
    ))

# 24 Waves distribution:
# Waves 1-4: 6 vids each (Clips 1-24)
# Waves 5-20: 4 vids each (Clips 25-88)
# Waves 21-24: 3 vids each (Clips 89-100)
wave_counts = [6]*4 + [4]*16 + [3]*4

start_dt_ist = datetime(2026, 11, 23, 13, 30)

waves = []
clip_counter = 1

for w_idx, count in enumerate(wave_counts, start=1):
    w_dt_ist = start_dt_ist + timedelta(minutes=(w_idx - 1) * 30)
    w_dt_utc = w_dt_ist - timedelta(hours=5, minutes=30)
    pub_ist = w_dt_ist.strftime("%d-%b-%Y %I:%M %p IST")
    pub_utc = w_dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    wave_videos = []
    for _ in range(count):
        idx = clip_counter
        hook_title, title = VIRAL_HOOKS[idx - 1]
        
        # Sourcing:
        # Clips 1-24: from source_speed_stream_36min.mp4 (0 to 2160s)
        # Clips 25-100: from source_speed_stream_part2.mp4 (0 to 6840s)
        if idx <= 24:
            source_file = r"d:\vidclip\storage\review_cuts\source_speed_stream_36min.mp4"
            start_sec = (idx - 1) * 90.0
        else:
            source_file = r"d:\vidclip\storage\review_cuts\source_speed_stream_part2.mp4"
            start_sec = (idx - 25) * 90.0

        wave_videos.append({
            "id": f"speed_clip_{idx:03d}",
            "index": idx,
            "source_file": source_file,
            "start_sec": start_sec,
            "duration": 90.0,
            "hook_title": hook_title,
            "title": title,
            "description": f"{title}\n\nWatch IShowSpeed live in GTA 6 Vice City! Rendered in 2K vertical layout with NeuralClips.\n\n#IShowSpeed #GTA6 #Shorts #Gaming #GTAOnline #ViceCity",
            "tags": ["IShowSpeed", "GTA6", "Speed GTA 6", "Shorts", "Gaming", "GTA 6 funny moments", "Vice City"]
        })
        clip_counter += 1

    waves.append({
        "wave_id": w_idx,
        "wave_name": f"Wave {w_idx:02d} ({w_dt_ist.strftime('%I:%M %p IST')})",
        "publish_at_ist": pub_ist,
        "publish_at_utc": pub_utc,
        "videos": wave_videos
    })

content = f'''"""Master Manifest for 24 Waves (100 Videos) of IShowSpeed up to 1:00 AM.
Auto-generated for exact 30-minute cadence and 100% daily YouTube upload quota saturation.
"""

from pathlib import Path

OUTPUT_DIR = r"d:\\vidclip\\storage\\batch_ishowspeed"
THUMB_DIR = r"d:\\vidclip\\storage\\thumbnails_speed"

WAVES = {json.dumps(waves, indent=2)}
'''

with open(MANIFEST_PY, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Generated master manifest: {MANIFEST_PY} with {len(waves)} waves and {clip_counter - 1} videos!")

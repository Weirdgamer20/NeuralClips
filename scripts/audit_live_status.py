import json
import urllib.request
import re
from datetime import datetime, timezone, timedelta

def check_live_status():
    with open(str(BASE_DIR / "storage" / "famous_streamers_manifest.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    now_utc = datetime.now(timezone.utc)
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = now_utc.astimezone(ist_tz)
    print("=" * 65)
    print(f"📊 LIVE YOUTUBE CLIPS AUDIT — {now_ist.strftime('%d-%b-%Y %I:%M:%S %p IST')}")
    print("=" * 65)

    batches = data.get("batches", [])
    
    live_batches = []
    upcoming_batches = []
    
    for b in batches:
        b_num = b["batch_number"]
        sched_ist_str = b["scheduled_release_time_ist"]
        # parse scheduled time
        # format: '21-Nov-2026 10:00 AM IST'
        clean_str = sched_ist_str.replace(" IST", "")
        sched_dt = datetime.strptime(clean_str, "%d-%b-%Y %I:%M %p").replace(tzinfo=ist_tz)
        
        is_live = sched_dt <= now_ist
        b_info = {
            "batch": b_num,
            "scheduled_ist": sched_ist_str,
            "is_live": is_live,
            "videos": b.get("videos", [])
        }
        if is_live:
            live_batches.append(b_info)
        else:
            upcoming_batches.append(b_info)

    total_live_vids = sum(len(b["videos"]) for b in live_batches)
    total_upcoming_vids = sum(len(b["videos"]) for b in upcoming_batches)

    print(f"\n🟢 LIVE NOW ON YOUTUBE (Publicly Watchable): {len(live_batches)} Batches ({total_live_vids} Videos)")
    print(f"🟡 UPCOMING SCHEDULED: {len(upcoming_batches)} Batches ({total_upcoming_vids} Videos)\n")

    print("-" * 65)
    print("🔴 CURRENTLY LIVE BATCHES (Published & Viewable Right Now):")
    print("-" * 65)
    for b in live_batches:
        print(f"Batch {b['batch']:02d} (Released {b['scheduled_ist']}):")
        for v in b["videos"]:
            print(f"  • [{v['streamer']:13s}] https://www.youtube.com/shorts/{v['youtube_url'].split('/')[-1]} | {v['title'][:45]}...")
        print()

    print("-" * 65)
    print("⏳ NEXT UPCOMING BATCHES (Going Public Next):")
    print("-" * 65)
    for b in upcoming_batches[:4]:
        mins_left = int((datetime.strptime(b["scheduled_ist"].replace(" IST", ""), "%d-%b-%Y %I:%M %p").replace(tzinfo=ist_tz) - now_ist).total_seconds() / 60)
        print(f"Batch {b['batch']:02d} — Releases at {b['scheduled_ist']} (in ~{mins_left} mins):")
        for v in b["videos"]:
            print(f"  • [{v['streamer']:13s}] https://www.youtube.com/shorts/{v['youtube_url'].split('/')[-1]} | {v['title'][:45]}...")
        print()

if __name__ == "__main__":
    check_live_status()

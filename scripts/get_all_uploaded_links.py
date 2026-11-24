import json

def main():
    with open("d:/vidclip/storage/famous_streamers_manifest.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    batches = data.get("batches", [])
    all_videos = []
    for b in batches:
        b_num = b.get("batch_number")
        for v in b.get("videos", []):
            v["batch_num"] = b_num
            all_videos.append(v)
            
    uploaded = [v for v in all_videos if v.get("youtube_url")]
    print(f"Total Uploaded & Scheduled: {len(uploaded)}\n")
    
    by_streamer = {}
    for v in uploaded:
        s = v.get("streamer", "Unknown")
        by_streamer.setdefault(s, []).append(v)
        
    for streamer, v_list in by_streamer.items():
        print(f"==================================================")
        print(f"🎥 {streamer.upper()} ({len(v_list)} Videos Uploaded)")
        print(f"==================================================")
        for i, v in enumerate(v_list, 1):
            url = v["youtube_url"]
            title = v["title"]
            batch = v["batch_num"]
            sched = v.get("scheduled_for", "N/A")
            print(f"{i}. {url}")
            print(f"   Title: \"{title}\" (Batch {batch} | Scheduled: {sched})")
        print()

if __name__ == "__main__":
    main()

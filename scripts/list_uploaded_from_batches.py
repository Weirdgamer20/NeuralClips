import json

def main():
    with open("d:/vidclip/storage/famous_streamers_manifest.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    batches = data.get("batches", [])
    print(f"Total batches in manifest: {len(batches)}")
    
    all_videos = []
    for b in batches:
        vids = b.get("videos", [])
        for v in vids:
            v["batch_num"] = b.get("batch_number")
            v["scheduled_time"] = b.get("scheduled_release_time_ist")
            all_videos.append(v)
            
    uploaded = [v for v in all_videos if v.get("youtube_id")]
    print(f"Total videos: {len(all_videos)} | Uploaded with YouTube ID: {len(uploaded)}\n")
    
    by_creator = {}
    for v in uploaded:
        c = v.get("creator", "Unknown")
        by_creator.setdefault(c, []).append(v)
        
    for creator, v_list in by_creator.items():
        print(f"=== {creator.upper()} ({len(v_list)} uploaded) ===")
        for v in v_list:
            y_url = f"https://www.youtube.com/shorts/{v['youtube_id']}"
            print(f"• {y_url} | {v['title']} (Batch {v['batch_num']})")
        print()

if __name__ == "__main__":
    main()

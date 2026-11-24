import json

def main():
    with open("d:/vidclip/storage/famous_streamers_manifest.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    clips = data.get("clips", [])
    uploaded = [c for c in clips if c.get("youtube_id")]
    print(f"Total uploaded & live on YouTube: {len(uploaded)}\n")
    
    by_creator = {}
    for c in uploaded:
        creator = c.get("creator", "Unknown")
        by_creator.setdefault(creator, []).append(c)
        
    for creator, c_list in by_creator.items():
        print(f"=== {creator.upper()} ({len(c_list)} uploaded) ===")
        for item in c_list:
            y_url = f"https://www.youtube.com/shorts/{item['youtube_id']}"
            print(f"- {y_url} | {item['title']}")
        print()

if __name__ == "__main__":
    main()

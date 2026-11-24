import sys
sys.path.insert(0, "d:/vidclip")
from scripts.antigravity_chrome_mcp import call_mcp, navigate, get_page_snapshot

def inspect_joined_clipup():
    url = "https://contentrewards.com/c/campaigns/802cf95a-ea84-4070-9a96-8a917831cb16"
    print(f"🚀 Navigating Tab 4 to {url}...")
    navigate(4, url)
    import time
    time.sleep(3)
    snap = get_page_snapshot(4)
    with open("d:/vidclip/storage/clipup_campaign_snapshot.txt", "w", encoding="utf-8") as f:
        f.write(snap)
    print(f"Saved snapshot ({len(snap)} bytes) to storage/clipup_campaign_snapshot.txt")
    for line in snap.splitlines():
        if any(k in line.lower() for k in ["rule", "brief", "logo", "file", "submit", "caption", "hashtag"]):
            print("  ", line)

if __name__ == "__main__":
    inspect_joined_clipup()

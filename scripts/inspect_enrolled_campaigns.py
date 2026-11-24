import sys
sys.path.insert(0, "d:/vidclip")
from scripts.antigravity_chrome_mcp import call_mcp, get_page_snapshot, click, fill, navigate

def main():
    print("=" * 60)
    print("🔍 INSPECTING ENROLLED CAMPAIGNS ON CONTENT REWARDS")
    print("=" * 60)
    
    # Take fresh snapshot of Tab 4
    snap = get_page_snapshot(4)
    print("Snapshot snippet around campaigns:")
    for line in snap.splitlines():
        if any(k in line.lower() for k in ["preview", "kai", "clipup", "wiped", "submit", "campaign", "search"]):
            print("  ", line)

if __name__ == "__main__":
    main()

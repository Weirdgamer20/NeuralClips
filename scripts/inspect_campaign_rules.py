from playwright.sync_api import sync_playwright

def inspect_rules(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        text = page.inner_text("body")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        print(f"\n=== RULES FOR {url.split('?')[0].split('/')[-1]} ===")
        # Look for brief, rules, files
        for i, l in enumerate(lines):
            if any(k in l.lower() for k in ["brief", "rule", "logo", "reference", "hashtag", "caption"]):
                print(f"[{i}] {l}")
                for sub in lines[max(0, i-2):min(len(lines), i+8)]:
                    print("   ", sub)
                print("-" * 40)
        browser.close()

if __name__ == "__main__":
    inspect_rules("https://contentrewards.com/c/campaigns/802cf95a-ea84-4070-9a96-8a917831cb16")
    inspect_rules("https://contentrewards.com/c/campaigns/cdf6dc09-a0ba-4fe8-8c6d-114773714557")

from playwright.sync_api import sync_playwright

def inspect_campaign(url):
    print("=" * 60)
    print(f"🔍 INSPECTING: {url}")
    print("=" * 60)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        print("Title:", page.title())
        text = page.inner_text("body")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for line in lines[:40]:
            print("  ", line)
        browser.close()

if __name__ == "__main__":
    inspect_campaign("https://contentrewards.com/c/campaigns/802cf95a-ea84-4070-9a96-8a917831cb16?src=share&sid=F0IRIkqcCanY")
    inspect_campaign("https://contentrewards.com/c/campaigns/cdf6dc09-a0ba-4fe8-8c6d-114773714557?src=share&sid=rEXz9BOZkbQb")

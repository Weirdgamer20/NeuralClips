from playwright.sync_api import sync_playwright
import json

def get_all_campaigns():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://contentrewards.com/c/discover", wait_until="networkidle")
        
        # Extract cards
        cards = page.eval_on_selector_all("a[href*='/c/']", """elements => {
            return elements.map(el => {
                const text = el.innerText.trim();
                const href = el.href;
                return { text, href };
            });
        }""")
        
        campaigns = []
        for c in cards:
            if "/c/discover" not in c['href'] and "/c/get-started" not in c['href']:
                lines = [l.strip() for l in c['text'].split('\n') if l.strip()]
                if len(lines) >= 2:
                    campaigns.append({
                        "title": lines[0] if len(lines) > 0 else "Unknown",
                        "details": lines,
                        "url": c['href']
                    })
        
        print(f"Total campaigns found: {len(campaigns)}")
        for i, camp in enumerate(campaigns[:10], 1):
            print(f"[{i}] {camp['details']}")
            print(f"    URL: {camp['url']}")
        
        browser.close()

if __name__ == "__main__":
    get_all_campaigns()

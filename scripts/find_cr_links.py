from playwright.sync_api import sync_playwright

def find_links():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://contentrewards.com", wait_until="networkidle")
        links = page.eval_on_selector_all("a", "elements => elements.map(e => ({text: e.innerText.trim(), href: e.href}))")
        for l in links:
            if l['text'] or l['href']:
                print(f"{l['text']} -> {l['href']}")
        browser.close()

if __name__ == "__main__":
    find_links()

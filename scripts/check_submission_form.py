from playwright.sync_api import sync_playwright
import re

def check_submission_form():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://contentrewards.com/c/campaigns/1d2bcb00-c904-415f-aa82-f95b96baad86"
        page.goto(url, wait_until="networkidle")
        
        # Check buttons, forms, inputs
        buttons = page.eval_on_selector_all("button", "els => els.map(e => e.innerText.trim())")
        print("Buttons found:", buttons)
        
        inputs = page.eval_on_selector_all("input", "els => els.map(e => ({placeholder: e.placeholder, name: e.name, type: e.type}))")
        print("Inputs found:", inputs)
        
        # Check if there is an API or modal for 'Submit' or 'Join'
        html = page.content()
        submit_endpoints = set(re.findall(r'[\'"][^\'"]*submit[^\'"]*[\'"]', html, re.I))
        print("Submit mentions:", list(submit_endpoints)[:10])
        
        browser.close()

if __name__ == "__main__":
    check_submission_form()

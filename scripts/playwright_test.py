from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto("https://google.com")

    page.locator('textarea[name="q"]').fill("RTX 5090 benchmarks")

    page.keyboard.press("Enter")

    input("Press Enter to close...")
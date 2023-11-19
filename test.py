from playwright.sync_api import sync_playwright

from routines import extract_title_details, get_repda, go_to_title_details

from pprint import pprint

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=False,
    )
    context = browser.new_context()
    context.set_default_timeout(60000)
    page = context.new_page()
    get_repda(page)
    go_to_title_details(page, "08GUA100304/12HMDL16")
    data = extract_title_details(page, "22/02/2022")
    pprint([d.num for d in data])
    page.wait_for_timeout(15000)

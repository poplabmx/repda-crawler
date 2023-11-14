from playwright.sync_api import sync_playwright

from routines import extract_title_details, get_repda, go_to_title_details

from pprint import pprint

with sync_playwright() as playwright:
    browser, context, page = get_repda(playwright)
    go_to_title_details(page, "815222")
    data = extract_title_details(page, "22/02/2022")
    pprint(data[0].json())
    page.wait_for_timeout(15000)

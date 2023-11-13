import playwright
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    # Open new page
    page = context.new_page()
    page.goto("https://app.conagua.gob.mx/consultarepda.aspx")
    page.get_by_role("textbox", name="Debes ingresar el número completo del título de concesión/asignación/permiso para realizar una búsqueda válida, este filtro no se combina con el nombre del titular.").click()
    page.get_by_role("textbox", name="Debes ingresar el número completo del título de concesión/asignación/permiso para realizar una búsqueda válida, este filtro no se combina con el nombre del titular.").fill("815222")
    page.get_by_role("button", name="Buscar").click()
    columnheader =     page.get_by_role("columnheader", name="Titular")
    page.wait_for_timeout(15000)

    print(columnheader.text_content())

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

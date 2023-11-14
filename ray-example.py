import ray

from playwright.sync_api import Playwright, sync_playwright, expect

ray.init(
    num_cpus=4,
)


@ray.remote
def run():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        # Open new page
        page = context.new_page()
        page.goto("https://app.conagua.gob.mx/consultarepda.aspx")
        page.get_by_role(
            "textbox",
            name="Debes ingresar el número completo del título de concesión/asignación/permiso para realizar una búsqueda válida, este filtro no se combina con el nombre del titular.",
        ).click()
        page.get_by_role(
            "textbox",
            name="Debes ingresar el número completo del título de concesión/asignación/permiso para realizar una búsqueda válida, este filtro no se combina con el nombre del titular.",
        ).fill("815222")
        page.get_by_role("button", name="Buscar").click()
        columnheader = page.get_by_role("columnheader", name="Titular")
        text = columnheader.text_content()
        page.wait_for_timeout(15000)
        page.goto("https://app.conagua.gob.mx/consultarepda.aspx")
        page.get_by_role(
            "textbox",
            name="Debes ingresar el número completo del título de concesión/asignación/permiso para realizar una búsqueda válida, este filtro no se combina con el nombre del titular.",
        ).click()
        page.get_by_role(
            "textbox",
            name="Escribe parcial o completamente el nombre del titular (es).",
        ).click()
        page.get_by_role(
            "textbox",
            name="Escribe parcial o completamente el nombre del titular (es).",
        ).fill("jorge")
        page.get_by_role("button", name="Buscar").click()
        page.get_by_role("cell", name="822381").click()
        page.get_by_text("Subterráneos", exact=True).click()

        print(columnheader)

        # ---------------------
        context.close()
        browser.close()

        return text


results = []

for i in range(4):
    results.append(run.remote())

print(ray.get(results))

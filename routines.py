from playwright.sync_api import Page, Playwright, expect
from data import DataItem

# import pretty print


def get_repda(page: Page):
    # Open new page
    page.goto("https://app.conagua.gob.mx/consultarepda.aspx")
    page.wait_for_load_state("networkidle")


def go_to_title_details(page: Page, title: str):
    page.get_by_role(
        "textbox",
        name="Debes ingresar el número completo del título de concesión/asignación/permiso para realizar una búsqueda válida, este filtro no se combina con el nombre del titular.",
    ).click()
    page.get_by_role(
        "textbox",
        name="Debes ingresar el número completo del título de concesión/asignación/permiso para realizar una búsqueda válida, este filtro no se combina con el nombre del titular.",
    ).fill(title)
    page.get_by_role("button", name="Buscar").click()
    page.wait_for_load_state("networkidle")
    # select anchor with the title as inner text
    title_details_link = page.locator("a#ContentPlaceHolder1_GVRepda_lnkDetalles_0")
    title_details_link.click()


def extract_title_details(page: Page, date: str) -> list[DataItem]:
    extracted_data = []

    main_info = extract_main_info(page)

    if int(main_info["anexos_superficiales"]) > 0:
        page.locator("#ContentPlaceHolder1_RadioTipoAprovechamiento1_0").click()
        surface_info = extract_surface(page)
        for dataitem in surface_info:
            extracted_data.append(
                DataItem(
                    **main_info, **dataitem, tipo_de_anexo="superficial", fecha=date
                )
            )

    if int(main_info["anexos_subterraneos"]) > 0:
        page.locator("#ContentPlaceHolder1_RadioTipoAprovechamiento1_1").click()
        subterranean_info = extract_subterranean(page)
        for dataitem in subterranean_info:
            extracted_data.append(
                DataItem(
                    **main_info, **dataitem, tipo_de_anexo="subterraneo", fecha=date
                )
            )

    if int(main_info["anexos_descargas"]) > 0:
        page.locator("#ContentPlaceHolder1_RadioTipoAprovechamiento1_2").click()
        discharges_info = extract_discharges(page)
        for dataitem in discharges_info:
            extracted_data.append(
                DataItem(**main_info, **dataitem, tipo_de_anexo="descarga", fecha=date)
            )

    if int(main_info["anexos_zonas_federales"]) > 0:
        page.locator("#ContentPlaceHolder1_RadioTipoAprovechamiento1_3").click()
        federal_zones_info = extract_federal_zones(page)
        for dataitem in federal_zones_info:
            extracted_data.append(
                DataItem(**main_info, **dataitem, tipo_de_anexo="federal", fecha=date)
            )

    return extracted_data


def extract_main_info(page: Page):
    # select the table with the main info
    return dict(
        titulo=page.locator("#ContentPlaceHolder1_LblTitulo").inner_text(),
        titular=page.locator("#ContentPlaceHolder1_LblTitular").inner_text(),
        uso_amparado=page.locator("#ContentPlaceHolder1_LblUso").inner_text(),
        volumen_total_de_aguas_nacionales=page.locator(
            "#ContentPlaceHolder1_LblVolumenAnual"
        ).inner_text(),
        volumen_total_de_aguas_superficiales=page.locator(
            "#ContentPlaceHolder1_LblVolSuperficial"
        ).inner_text(),
        volumen_total_de_aguas_subterraneas=page.locator(
            "#ContentPlaceHolder1_LblVolSuperficial"
        ).inner_text(),
        volumen_total_de_descargas=page.locator(
            "#ContentPlaceHolder1_LblVolDescarga"
        ).inner_text(),
        anexos_superficiales=page.locator(
            "#ContentPlaceHolder1_LblAprovSuperficial"
        ).inner_text(),
        anexos_subterraneos=page.locator(
            "#ContentPlaceHolder1_LblAprovSubterraneo"
        ).inner_text(),
        anexos_zonas_federales=page.locator(
            "#ContentPlaceHolder1_LblZonaFederal"
        ).inner_text(),
        anexos_descargas=page.locator("#ContentPlaceHolder1_LblDescarga").inner_text(),
        superficie_total=page.locator(
            "#ContentPlaceHolder1_LblVolZonaFederal"
        ).inner_text(),
        anotaciones_marginales=page.locator(
            "#ContentPlaceHolder1_LblMarginalF1"
        ).inner_text(),
    )


def extract_subterranean(page: Page):
    # select the table with the subterranean info
    table = page.locator("#ContentPlaceHolder1_GVSubterraneosF1")
    table.locator("th").first.wait_for()
    table.locator("td").first.wait_for()
    table_rows = table.locator("tr").all()

    pages = table_rows[0].locator("a").all()
    num_pages = len(pages) + 1

    if num_pages > 1:
        table_rows = table_rows[3:-2]
    else:
        table_rows = table_rows[1:]

    table_data = []

    for page_num in range(num_pages):
        for row in table_rows:
            row_data = row.locator("td").all()
            table_data.append(
                dict(
                    num=row_data[0].inner_text(),
                    lat=row_data[1].inner_text(),
                    lon=row_data[2].inner_text(),
                    estado=row_data[3].inner_text(),
                    municipio=row_data[4].inner_text(),
                    region_hidrologica=row_data[5].inner_text(),
                    cuenca=row_data[6].inner_text(),
                    acuifero=row_data[7].inner_text(),
                    acuifero_homologado=row_data[8].inner_text(),
                    volumen=row_data[9].inner_text(),
                )
            )
        if num_pages > 1 and page_num < num_pages - 1:
            # elemnts 11, 21, etc appear as "..." in the page
            if page_num > 1 and (page_num + 2) % 10 == 1:
                print("page link with ...")
                page_link = table.locator("a", has_text="...")
            else:
                print(f"page link with {page_num + 2}")
                page_link = table.locator("a", has_text=str(page_num + 2))
            print(f"Page link {page_link.first.inner_text()}")
            page_link.first.click()
            print(f'waiting for element with text "{(page_num+1)*5 + 1}"')
            page.wait_for_load_state("networkidle")
            table.locator("tr").all()[3].get_by_role(
                "cell", name=f"{(page_num+1)*5 + 1}", exact=True
            ).wait_for()
            table = page.locator("#ContentPlaceHolder1_GVSubterraneosF1")
            table_rows = table.locator("tr").all()[3:-2]
    return table_data


def extract_surface(page: Page):
    # select the table with the surface info
    table = page.locator("#ContentPlaceHolder1_GVSuperficialesF1")
    table.locator("th").first.wait_for()
    table.locator("td").first.wait_for()
    table_rows = table.locator("tr").all()

    pages = table_rows[0].locator("a").all()
    num_pages = len(pages) + 1

    if num_pages > 1:
        table_rows = table_rows[3:-2]
    else:
        table_rows = table_rows[1:]

    table_data = []

    for page_num in range(num_pages):
        for row in table_rows:
            row_data = row.locator("td").all()
            table_data.append(
                dict(
                    num=row_data[0].inner_text(),
                    lat=row_data[1].inner_text(),
                    lon=row_data[2].inner_text(),
                    estado=row_data[3].inner_text(),
                    municipio=row_data[4].inner_text(),
                    region_hidrologica=row_data[5].inner_text(),
                    cuenca=row_data[6].inner_text(),
                    fuente=row_data[7].inner_text(),
                    afluente=row_data[8].inner_text(),
                    volumen=row_data[9].inner_text(),
                )
            )
        if num_pages > 1 and page_num < num_pages - 1:
            if page_num > 1 and (page_num + 2) % 10 == 1:
                page_link = table.locator("a", has_text="...")
            else:
                page_link = table.locator("a", has_text=str(page_num + 2))
            print(f"Page link {page_link.first.inner_text()}")
            page_link.first.click()
            print(f'waiting for element with text "{(page_num+1)*5 + 1}"')
            page.wait_for_load_state("networkidle")
            table.locator("tr").all()[3].get_by_role(
                "cell", name=f"{(page_num+1)*5 + 1}", exact=True
            ).wait_for()
            table = page.locator("#ContentPlaceHolder1_GVSuperficialesF1")
            table_rows = table.locator("tr").all()[3:-2]
    return table_data


def extract_federal_zones(page: Page):
    # select the table with the federal zones info
    table = page.locator("#ContentPlaceHolder1_GVFederalesF1")
    table.locator("th").first.wait_for()
    table.locator("td").first.wait_for()
    table_rows = table.locator("tr").all()
    pages = table_rows[0].locator("a").all()
    num_pages = len(pages) + 1

    # print(f"pages in anexos_zonas_federales: {num_pages}")
    if num_pages > 1:
        table_rows = table_rows[3:-2]
    else:
        table_rows = table_rows[1:]

    table_data = []

    for page_num in range(num_pages):
        # print(f"Page {page_num + 1}")
        # print(f"Num pages {num_pages}")
        # print(f"Table rows {len(table_rows)}")
        for row in table_rows:
            row_data = row.locator("td").all()
            table_data.append(
                dict(
                    num=row_data[0].inner_text(),
                    lat=row_data[1].inner_text(),
                    lon=row_data[2].inner_text(),
                    estado=row_data[3].inner_text(),
                    municipio=row_data[4].inner_text(),
                    region_hidrologica=row_data[5].inner_text(),
                    cuenca=row_data[6].inner_text(),
                    corriente_o_vaso=row_data[7].inner_text(),
                    superficie=row_data[8].inner_text(),
                )
            )

        if num_pages > 1 and page_num < num_pages - 1:
            if page_num > 1 and (page_num + 2) % 10 == 1:
                page_link = table.locator("a", has_text="...")
            else:
                page_link = table.locator("a", has_text=str(page_num + 2))
            # print(f"Page link {page_link.first.inner_text()}")
            page_link.first.click()
            # print(f'waiting for element with text "{(page_num+1)*5 + 1}"')
            page.wait_for_load_state("networkidle")
            table.locator("tr").all()[3].get_by_role(
                "cell", name=f"{(page_num+1)*5 + 1}", exact=True
            ).wait_for()
            table = page.locator("#ContentPlaceHolder1_GVFederalesF1")
            table_rows = table.locator("tr").all()[3:-2]
    return table_data


def extract_discharges(page: Page):
    table = page.locator("#ContentPlaceHolder1_GVResidualesF1")
    table.locator("th").first.wait_for()
    table.locator("td").first.wait_for()
    table_rows = table.locator("tr").all()

    pages = table_rows[0].locator("a").all()
    num_pages = len(pages) + 1

    if num_pages > 1:
        table_rows = table_rows[3:-2]
    else:
        table_rows = table_rows[1:]

    table_data = []

    for page_num in range(num_pages):
        for row in table_rows:
            row_data = row.locator("td").all()
            table_data.append(
                dict(
                    num=row_data[0].inner_text(),
                    lat=row_data[1].inner_text(),
                    lon=row_data[2].inner_text(),
                    estado=row_data[3].inner_text(),
                    municipio=row_data[4].inner_text(),
                    region_hidrologica=row_data[5].inner_text(),
                    cuenca=row_data[6].inner_text(),
                    cuerpo_receptor=row_data[7].inner_text(),
                    descarga_afluente=row_data[8].inner_text(),
                    procedencia=row_data[9].inner_text(),
                    forma_de_descarga=row_data[10].inner_text(),
                    tipo_de_descarga=row_data[11].inner_text(),
                    volumen_de_descarga_diario=row_data[12].inner_text(),
                    volumen_de_descarga_anual=row_data[13].inner_text(),
                )
            )
        if num_pages > 1 and page_num < num_pages - 1:
            if page_num > 1 and (page_num + 2) % 10 == 1:
                print("page link with ...")
                page_link = table.locator("a", has_text="...")
            else:
                print(f"page link with {page_num + 2}")
                page_link = table.locator("a", has_text=str(page_num + 2))
            print(f"Page link {page_link.first.inner_text()} found")
            page_link.first.click()
            print(f'waiting for element with text "{(page_num+1)*5 + 1}"')
            page.wait_for_load_state("networkidle")
            table.locator("tr").all()[3].get_by_role(
                "cell", name=f"{(page_num+1)*5 + 1}", exact=True
            ).wait_for()
            print("element found")
            table = page.locator("#ContentPlaceHolder1_GVResidualesF1")
            table_rows = table.locator("tr").all()[3:-2]

    return table_data

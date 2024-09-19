import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def run(playwright):
    # Lanzar el navegador (headless=False para ver la ejecución)
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Crear una nueva página
    page = await context.new_page()

    # Navegar a la página de búsqueda en SIPC con el término 'finance'
    search_url = 'https://www.sipc.org/search?query=finance'
    print(f"Accediendo a la URL: {search_url}")
    await page.goto(search_url)

    # Esperar a que aparezcan los resultados de búsqueda
    await page.wait_for_selector('div.border-top.border-light')  # Selector para los resultados de búsqueda

    # Extraer todos los resultados de búsqueda
    articles = await page.query_selector_all('div.border-top.border-light')

    # Limitar a los primeros 3 resultados
    num_results = min(len(articles), 3)
    print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results}.")

    # Lista para almacenar los datos extraídos
    data = []

    for i in range(num_results):
        article = articles[i]

        # Extraer el título del artículo
        headline_element = await article.query_selector('strong > a')
        if headline_element:
            headline_text = await headline_element.inner_text()
            link = await headline_element.get_attribute('href')  # Extraer el enlace del artículo
        else:
            headline_text = "No disponible"
            link = "No disponible"

        # Extraer la fecha del artículo
        date_element = await article.query_selector('em')
        if date_element:
            published_date = await date_element.inner_text()
        else:
            published_date = "No disponible"

        # Extraer la descripción del artículo
        description_elements = await article.query_selector_all('p.small')
        description_text = " ".join([await desc.inner_text() for desc in description_elements])

        print(f"Resultado {i+1}:")
        print(f"Título: {headline_text}")
        print(f"Fecha: {published_date}")
        print(f"Enlace: {link}")
        print(f"Descripción: {description_text[:100]}...")  # Mostrar los primeros 100 caracteres del contenido

        # Almacenar los datos en un diccionario
        data.append({
            'title': headline_text,
            'published_date': published_date,
            'link': f"https://www.sipc.org{link}",
            'description': description_text
        })

    # Convertir los datos a un DataFrame y guardarlos en un CSV
    df = pd.DataFrame(data)
    df.to_csv('sipc_search_results.csv', index=False)
    print('Datos guardados en sipc_search_results.csv')

    # Cerrar el navegador
    await browser.close()

# Ejecutar Playwright de manera asíncrona
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

# Iniciar la ejecución
asyncio.run(main())

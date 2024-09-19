import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def run(playwright):
    # Lanzar el navegador (headless=False para ver la ejecución)
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Crear una nueva página
    page = await context.new_page()

    # Navegar a la página de búsqueda en NerdWallet con el término 'finance'
    search_url = 'https://www.nerdwallet.com/search/results?q=finance'
    print(f"Accediendo a la URL: {search_url}")
    await page.goto(search_url)

    # Esperar a que aparezcan los resultados de búsqueda
    await page.wait_for_selector('li div._2vpLU_')  # Selector para los resultados de búsqueda

    # Extraer todos los resultados de búsqueda
    articles = await page.query_selector_all('li div._2vpLU_')

    # Limitar a los primeros 3 resultados
    num_results = min(len(articles), 3)
    print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results}.")

    # Lista para almacenar los datos extraídos
    data = []

    for i in range(num_results):
        article = articles[i]

        # Extraer el título del artículo
        headline_element = await article.query_selector('h3.zeCuXk > a')
        if headline_element:
            headline_text = await headline_element.inner_text()
            link = await headline_element.get_attribute('href')  # Extraer el enlace del artículo
        else:
            headline_text = "No disponible"
            link = "No disponible"

        # Extraer la fecha del artículo
        date_element = await article.query_selector('span._1xAKS5')
        if date_element:
            published_date = await date_element.inner_text()
        else:
            published_date = "No disponible"

        # Extraer la descripción del artículo
        description_element = await article.query_selector('span._2LuWPZ._28z5Fp')
        if description_element:
            description_text = await description_element.inner_text()
        else:
            description_text = "No disponible"

        # Abrir la página del artículo para extraer su contenido
        if link != "No disponible":
            article_page = await context.new_page()
            try:
                # Navegar a la página del artículo
                await article_page.goto(link, wait_until="domcontentloaded", timeout=60000)

                # Esperar a que el contenido del artículo esté cargado
                await article_page.wait_for_selector('div#page-content')

                # Extraer todo el contenido del artículo
                paragraphs = await article_page.query_selector_all('div#page-content p')
                content_text = "\n".join([await p.inner_text() for p in paragraphs])

            except Exception as e:
                print(f"Error al cargar el artículo {i+1}: {e}")
                content_text = "Error al cargar el contenido"

            # Cerrar la página del artículo
            await article_page.close()
        else:
            content_text = "No disponible"

        print(f"Resultado {i+1}:")
        print(f"Título: {headline_text}")
        print(f"Fecha: {published_date}")
        print(f"Descripción: {description_text}")
        print(f"Enlace: {link}")
        print(f"Contenido: {content_text[:100]}...")  # Mostrar los primeros 100 caracteres del contenido

        # Almacenar los datos en un diccionario
        data.append({
            'title': headline_text,
            'published_date': published_date,
            'description': description_text,
            'link': link,
            'content': content_text
        })

    # Convertir los datos a un DataFrame y guardarlos en un CSV
    df = pd.DataFrame(data)
    df.to_csv('nerdwallet_search_results.csv', index=False)
    print('Datos guardados en nerdwallet_search_results.csv')

    # Cerrar el navegador
    await browser.close()

# Ejecutar Playwright de manera asíncrona
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

# Iniciar la ejecución
asyncio.run(main())

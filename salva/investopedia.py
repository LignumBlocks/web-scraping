import asyncio
from playwright.async_api import async_playwright
import pandas as pd

video_id = "@hermoneymastery_video_7301700833052314922"
# Lista de consultas
queries = ['Snowball debt payoff method effectiveness', 'Avalanche debt payoff method comparison', 'personalized debt payoff plan best practices', 'budgeting for extra debt payments strategies']


async def run(playwright):
    # Lanzar el navegador (headless=False para ver la ejecución)
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Lista para almacenar los datos extraídos de todas las consultas
    all_data = []

    # Iterar sobre cada consulta en la lista de queries
    for query in queries:
        # Formatear la URL de búsqueda con la consulta
        search_url = f'https://www.investopedia.com/search?q={query.replace(" ", "%20")}'
        print(f"Accediendo a la URL: {search_url}")
        page = await context.new_page()
        await page.goto(search_url)

        # Esperar a que aparezcan los resultados de búsqueda
        await page.wait_for_selector('div.search-results__list')  # Ajuste según el HTML proporcionado

        # Extraer todos los resultados de búsqueda
        articles = await page.query_selector_all('div.search-results__list')

        # Limitar a los primeros 3 resultados
        num_results = min(len(articles), 3)
        print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results} para la query: '{query}'.")

        for i in range(num_results):
            article = articles[i]

            # Extraer el título del artículo
            headline_element = await article.query_selector('h3.search-results__title')
            if headline_element:
                headline_text = await headline_element.inner_text()
                link_element = await article.query_selector('a.search-results__link')
                link = await link_element.get_attribute('href') if link_element else "No disponible"
            else:
                headline_text = "No disponible"
                link = "No disponible"

            # Extraer la descripción del artículo
            description_element = await article.query_selector('div.search-results__description')
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
                    await article_page.wait_for_selector('div.article-body-content')

                    # Extraer todo el contenido del artículo
                    paragraphs = await article_page.query_selector_all('div.article-body-content > p.mntl-sc-block-html')
                    content_text = "\n".join([await p.inner_text() for p in paragraphs])

                except Exception as e:
                    print(f"Error al cargar el artículo {i+1} para la query '{query}': {e}")
                    content_text = "Error al cargar el contenido"

                # Cerrar la página del artículo
                await article_page.close()
            else:
                content_text = "No disponible"

            print(f"Resultado {i+1}:")
            print(f"Título: {headline_text}")
            print(f"Descripción: {description_text}")
            print(f"Enlace: {link}")
            print(f"Contenido: {content_text[:100]}...")  # Mostrar los primeros 100 caracteres del contenido

            # Almacenar los datos en un diccionario
            all_data.append({
                'query': query,
                'title': headline_text,
                'description': description_text,
                'link': link,
                'content': content_text
            })

        # Cerrar la página de búsqueda para esta query
        await page.close()

    # Convertir los datos a un DataFrame y guardarlos en un solo CSV
    df = pd.DataFrame(all_data)
    df.to_csv(f'investopedia_{video_id}.csv', index=False)
    print(f'Datos guardados en investopedia_{video_id}.csv')

    # Cerrar el navegador
    await browser.close()

# Ejecutar Playwright de manera asíncrona
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

# Iniciar la ejecución
asyncio.run(main())

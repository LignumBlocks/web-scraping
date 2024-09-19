import asyncio
from playwright.async_api import async_playwright
import pandas as pd


video_id = "@hermoneymastery_video_7301700833052314922"
# Lista de consultas
queries = ['Snowball debt payoff method effectiveness', 'Avalanche debt payoff method comparison', 'personalized debt payoff plan best practices', 'budgeting for extra debt payments strategies']

async def run(playwright):
    # Lanzar el navegador (headless=False si quieres ver la ejecución)
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Lista para almacenar los datos extraídos de todas las consultas
    all_data = []

    # Iterar sobre cada consulta en la lista de queries
    for query in queries:
        # Formatear la URL de búsqueda con la consulta
        search_url = f'https://www.forbes.com/search/?q={query.replace(" ", "%20")}'
        print(f"Accediendo a la URL: {search_url}")
        page = await context.new_page()
        await page.goto(search_url)

        # Esperar a que aparezcan los resultados de búsqueda
        await page.wait_for_selector('div.CardArticle_wrapper__MpbGX > div > a:first-child')

        # Extraer todos los elementos de artículos que contienen tanto el título como la descripción
        articles = await page.query_selector_all('div.CardArticle_wrapper__MpbGX > div > a:first-child')

        # Limitar a los primeros 3 resultados
        num_results = min(len(articles), 3)
        print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results} para la query: '{query}'.")

        for i in range(num_results):
            article = articles[i]
            
            # Extraer el texto del título del artículo
            headline_element = await article.query_selector('h3.CardArticle_headline___NhjF')
            if headline_element:
                headline_text = await headline_element.inner_text()
            else:
                headline_text = "No disponible"

            # Extraer el texto de la descripción del artículo
            description_element = await article.query_selector('p.CardArticle_description__2fQbs')
            if description_element:
                description_text = await description_element.inner_text()
            else:
                description_text = "No disponible"

            # Extraer el enlace del artículo
            link = await article.get_attribute('href')
            if not link:
                link = "No disponible"

            # Abrir la página del artículo para extraer su contenido
            if link != "No disponible":
                article_page = await context.new_page()
                try:
                    # Esperar a que solo el contenido HTML esté cargado
                    await article_page.goto(link, wait_until="domcontentloaded", timeout=60000)

                    # Esperar a que el contenido del artículo esté cargado (ajusta el selector si es necesario)
                    await article_page.wait_for_selector('div.article-body')

                    # Extraer el contenido del artículo
                    article_content_element = await article_page.query_selector('div.article-body')
                    if article_content_element:
                        article_content = await article_content_element.inner_text()
                    else:
                        article_content = "Contenido no disponible"

                except Exception as e:
                    print(f"Error al cargar el artículo {i+1} para la query '{query}': {e}")
                    article_content = "Error al cargar el contenido"

                # Cerrar la página del artículo
                await article_page.close()
            else:
                article_content = "No disponible"

            print(f"Resultado {i+1}:")
            print(f"Título: {headline_text}")
            print(f"Descripción: {description_text}")
            print(f"Enlace: {link}")
            print(f"Contenido: {article_content[:100]}...")  # Mostrar los primeros 100 caracteres del contenido

            # Almacenar los datos en un diccionario
            all_data.append({
                'query': query,
                'title': headline_text,
                'description': description_text,
                'link': link,
                'content': article_content
            })

        # Cerrar la página de búsqueda para esta query
        await page.close()

    # Convertir los datos a un DataFrame y guardarlos en un solo CSV
    df = pd.DataFrame(all_data)
    df.to_csv(f'forbes_{video_id}.csv', index=False)
    print(f'Datos guardados en forbes_{video_id}.csv')

    # Cerrar el navegador
    await browser.close()

# Ejecutar Playwright de manera asíncrona
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

# Iniciar la ejecución
asyncio.run(main())

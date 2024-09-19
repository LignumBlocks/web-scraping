import asyncio
from playwright.async_api import async_playwright
import pandas as pd

# Lista de consultas (queries)
queries = [
    "Financial Management Using Multiple Accounts"
]

async def run(playwright):
    # Lanzar el navegador (headless=False para ver la ejecución)
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Lista para almacenar los datos extraídos de todas las consultas
    all_data = []

    # Dominio base para Wikipedia
    base_url = "https://en.wikipedia.org"

    # Iterar sobre cada consulta en la lista de queries
    for query in queries:
        try:
            # Formatear la URL de búsqueda con la consulta en Wikipedia
            search_url = f'https://en.wikipedia.org/w/index.php?search={query.replace(" ", "+")}&title=Special%3ASearch&ns0=1'
            print(f"\nAccediendo a la URL: {search_url}")
            page = await context.new_page()
            await page.goto(search_url)

            # Verificar si hay resultados de búsqueda (timeout de 10 segundos)
            try:
                await page.wait_for_selector('ul.mw-search-results', timeout=10000)
            except Exception as e:
                print(f"No se encontraron resultados para la query '{query}'.")
                await page.close()
                continue  # Pasar a la siguiente consulta si no hay resultados

            # Extraer todos los resultados de búsqueda
            articles = await page.query_selector_all('ul.mw-search-results > li')

            # Limitar a los primeros 3 resultados
            num_results = min(len(articles), 3)
            print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results} para la query: '{query}'.")

            for i in range(num_results):
                article = articles[i]

                # Extraer el título del artículo
                headline_element = await article.query_selector('div.mw-search-result-heading a')
                headline_text = await headline_element.inner_text() if headline_element else "No disponible"

                # Extraer el enlace del artículo
                link = await headline_element.get_attribute('href') if headline_element else "No disponible"

                # Verificar si el enlace es relativo, y agregar el dominio base
                if link and link.startswith("/"):
                    link = base_url + link

                # Extraer la descripción del artículo (si está disponible)
                description_element = await article.query_selector('div.searchresult')
                description_text = await description_element.inner_text() if description_element else "No disponible"

                # Abrir la página del artículo para extraer su contenido
                content_text = "No disponible"
                if link != "No disponible":
                    article_page = await context.new_page()
                    try:
                        await article_page.goto(link, wait_until="domcontentloaded", timeout=60000)

                        # Esperar a que el contenido del artículo esté cargado
                        await article_page.wait_for_selector('div.mw-parser-output', timeout=10000)

                        # Extraer todo el contenido dentro de `div.mw-parser-output`
                        content_element = await article_page.query_selector('div.mw-parser-output')
                        content_text = await content_element.inner_text() if content_element else "Contenido no disponible"

                    except Exception as e:
                        print(f"Error al cargar el artículo {i+1} para la query '{query}': {e}")

                    # Cerrar la página del artículo
                    await article_page.close()

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

        except Exception as e:
            print(f"Error procesando la query '{query}': {e}")

    # Convertir los datos a un DataFrame y guardarlos en un solo CSV
    df = pd.DataFrame(all_data)
    df.to_csv('wikipedia_search_results.csv', index=False)
    print('Datos guardados en wikipedia_search_results.csv')

    # Cerrar el navegador
    await browser.close()

# Ejecutar Playwright de manera asíncrona
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

# Iniciar la ejecución
asyncio.run(main())

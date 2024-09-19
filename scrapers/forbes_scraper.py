# scrapers/forbes_scraper.py
import asyncio
from playwright.async_api import async_playwright

async def scrape_forbes(query):
    results = []
    print(f"Scraping Forbes for query: {query}")
    
    async with async_playwright() as playwright:
        # Lanzar el navegador (puedes cambiar headless=False si quieres ver el proceso)
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()

        # Crear una nueva página
        page = await context.new_page()

        # Construir la URL de búsqueda de Forbes
        search_url = f'https://www.forbes.com/search/?q={query.replace(" ", "%20")}'
        print(f"Accediendo a la URL de búsqueda de Forbes: {search_url}")
        
        try:
            await page.goto(search_url)

            # Esperar a que aparezcan los resultados de búsqueda
            await page.wait_for_selector('div.CardArticle_wrapper__MpbGX')

            # Extraer los primeros 3 resultados de búsqueda
            articles = await page.query_selector_all('div.CardArticle_wrapper__MpbGX > div > a:first-child')

            num_results = min(len(articles), 3)
            print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results}.")

            for i in range(num_results):
                article = articles[i]

                # Extraer el título del artículo
                headline_element = await article.query_selector('h3.CardArticle_headline___NhjF')
                headline_text = await headline_element.inner_text() if headline_element else "No disponible"

                # Extraer la descripción del artículo
                description_element = await article.query_selector('p.CardArticle_description__2fQbs')
                description_text = await description_element.inner_text() if description_element else "No disponible"

                # Extraer el enlace del artículo
                link = await article.get_attribute('href') if article else "No disponible"

                # Abrir la página del artículo para extraer el contenido
                content_text = "No disponible"
                if link != "No disponible":
                    article_page = await context.new_page()
                    try:
                        await article_page.goto(link, wait_until="domcontentloaded", timeout=60000)
                        await article_page.wait_for_selector('div.article-body')

                        # Extraer el contenido del artículo
                        content_element = await article_page.query_selector('div.article-body')
                        content_text = await content_element.inner_text() if content_element else "Contenido no disponible"

                    except Exception as e:
                        print(f"Error al cargar el artículo {i+1}: {e}")

                    await article_page.close()

                # Agregar los datos extraídos a los resultados
                results.append({
                    'query': query,
                    'source': 'forbes',
                    'title': headline_text,
                    'description': description_text,
                    'link': link,
                    'content': content_text
                })
        
        except Exception as e:
            print(f"Error durante la búsqueda de {query}: {e}")

        # Cerrar el navegador
        await browser.close()

    return results

# scrapers/marketwatch_scraper.py
import asyncio
from playwright.async_api import async_playwright

async def scrape_marketwatch(query):
    results = []
    print(f"Scraping MarketWatch for query: {query}")
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        search_url = f'https://www.marketwatch.com/search?q={query.replace(" ", "%20")}&tab=All%20News'
        print(f"Accediendo a la URL de búsqueda de MarketWatch: {search_url}")
        
        try:
            await page.goto(search_url)

            await page.wait_for_selector('div.article__content')

            articles = await page.query_selector_all('div.article__content')

            num_results = min(len(articles), 3)
            print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results}.")

            for i in range(num_results):
                article = articles[i]

                headline_element = await article.query_selector('h3.article__headline a')
                headline_text = await headline_element.inner_text() if headline_element else "No disponible"
                link = await headline_element.get_attribute('href') if headline_element else "No disponible"

                description_element = await article.query_selector('div.article__summary')
                description_text = await description_element.inner_text() if description_element else "No disponible"

                # Abrir la página del artículo para extraer el contenido
                content_text = "No disponible"
                if link != "No disponible":
                    article_page = await context.new_page()
                    try:
                        await article_page.goto(link, wait_until="domcontentloaded", timeout=60000)
                        await article_page.wait_for_selector('section.ef4qpkp0')  # Ajusta según el HTML

                        content_element = await article_page.query_selector('section.ef4qpkp0')
                        content_text = await content_element.inner_text() if content_element else "Contenido no disponible"

                    except Exception as e:
                        print(f"Error al cargar el artículo {i+1}: {e}")

                    await article_page.close()

                results.append({
                    'query': query,
                    'source': 'marketwatch',
                    'title': headline_text,
                    'description': description_text,
                    'link': link,
                    'content': content_text
                })
        
        except Exception as e:
            print(f"Error durante la búsqueda de {query}: {e}")

        await browser.close()

    return results

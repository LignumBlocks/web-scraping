# scrapers/consumer_finance_scraper.py
import asyncio
from playwright.async_api import async_playwright

async def scrape_consumer_finance(query):
    results = []
    print(f"Scraping Consumer Finance for query: {query}")
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        search_url = f'https://search.consumerfinance.gov/search?utf8=%E2%9C%93&affiliate=cfpb&query={query.replace(" ", "+")}'
        print(f"Accediendo a la URL de búsqueda de Consumer Finance: {search_url}")
        
        try:
            await page.goto(search_url)

            await page.wait_for_selector('div.content-block-item')

            articles = await page.query_selector_all('div.content-block-item')

            num_results = min(len(articles), 3)
            print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results}.")

            for i in range(num_results):
                article = articles[i]

                headline_element = await article.query_selector('h4.title a')
                headline_text = await headline_element.inner_text() if headline_element else "No disponible"
                link = await headline_element.get_attribute('href') if headline_element else "No disponible"

                description_element = await article.query_selector('span.description')
                description_text = await description_element.inner_text() if description_element else "No disponible"

                # Abrir la página del artículo para extraer el contenido
                content_text = "No disponible"
                if link != "No disponible":
                    article_page = await context.new_page()
                    try:
                        await article_page.goto(link, wait_until="domcontentloaded", timeout=60000)
                        await article_page.wait_for_selector('div.u-layout-grid__main')  # Ajusta este selector según la página

                        content_element = await article_page.query_selector('div.u-layout-grid__main')
                        content_text = await content_element.inner_text() if content_element else "Contenido no disponible"

                    except Exception as e:
                        print(f"Error al cargar el artículo {i+1}: {e}")

                    await article_page.close()

                results.append({
                    'query': query,
                    'source': 'consumer finance',
                    'title': headline_text,
                    'description': description_text,
                    'link': link,
                    'content': content_text
                })
        except Exception as e:
            print(f"Error durante la búsqueda de {query}: {e}")

        await browser.close()

    return results

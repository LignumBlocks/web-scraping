# scrapers/investopedia_scraper.py
import asyncio
from playwright.async_api import async_playwright

async def scrape_investopedia(query):
    results = []
    print(f"Scraping Investopedia for query: {query}")
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        search_url = f'https://www.investopedia.com/search?q={query.replace(" ", "+")}'
        print(f"Accediendo a la URL de búsqueda de Investopedia: {search_url}")
        
        try:
            await page.goto(search_url)

            await page.wait_for_selector('div.search-results__list')

            articles = await page.query_selector_all('div.search-results__list')

            num_results = min(len(articles), 3)
            print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results}.")

            for i in range(num_results):
                article = articles[i]

                headline_element = await article.query_selector('h3.search-results__title')
                headline_text = await headline_element.inner_text() if headline_element else "No disponible"
                link = await article.query_selector('a.search-results__link')
                link_href = await link.get_attribute('href') if link else "No disponible"

                description_element = await article.query_selector('div.search-results__description')
                description_text = await description_element.inner_text() if description_element else "No disponible"

                # Abrir la página del artículo para extraer el contenido
                content_text = "No disponible"
                if link_href != "No disponible":
                    article_page = await context.new_page()
                    try:
                        await article_page.goto(link_href, wait_until="domcontentloaded", timeout=60000)
                        await article_page.wait_for_selector('div.article-body-content')  # Ajusta según el HTML

                        content_element = await article_page.query_selector('div.article-body-content')
                        content_text = await content_element.inner_text() if content_element else "Contenido no disponible"

                    except Exception as e:
                        print(f"Error al cargar el artículo {i+1}: {e}")

                    await article_page.close()

                results.append({
                    'query': query,
                    'source': 'investopedia',
                    'title': headline_text,
                    'description': description_text,
                    'link': link_href,
                    'content': content_text
                })

            await browser.close()

        except Exception as e:
            print(f"Error durante la búsqueda de {query}: {e}")

    return results

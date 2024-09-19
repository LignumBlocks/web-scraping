# scrapers/the_balance_money_scraper.py
import asyncio
from playwright.async_api import async_playwright

async def scrape_the_balance_money(query):
    results = []
    print(f"Scraping The Balance Money for query: {query}")
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        search_url = f'https://www.thebalancemoney.com/search?q={query.replace(" ", "%20")}'
        print(f"Accediendo a la URL de búsqueda de The Balance Money: {search_url}")
        
        try:
            await page.goto(search_url)

            # Intentar esperar a que aparezcan los resultados de búsqueda (timeout de 10 segundos)
        
            await page.wait_for_selector('div.mntl-card-list', timeout=10000)  # Ajuste según el HTML de la página
        

            articles = await page.query_selector_all('a.mntl-card-list-items')

            num_results = min(len(articles), 3)
            print(f"Se encontraron {len(articles)} resultados, mostrando los primeros {num_results}.")

            for i in range(num_results):
                article = articles[i]

                # Extraer el título del artículo
                #headline_element = await article.query_selector('a.card-list-link')
                if article:
                    #headline_text = await headline_element.inner_text()
                    link = await article.get_attribute('href')
                else:
                    #headline_text = "No disponible"
                    link = "No disponible"
                
                # Extraer la descripción del artículo
                description_element = await article.query_selector('div.card-list-description')
                if description_element:
                    description_text = await description_element.inner_text()
                else:
                    description_text = "No disponible"

                # Abrir la página del artículo para extraer el contenido
                content_text = "No disponible"
                if link != "No disponible":
                    article_page = await context.new_page()
                    try:
                        await article_page.goto(link, wait_until="domcontentloaded", timeout=60000)
                        await article_page.wait_for_selector('div.article-content')  # Ajusta este selector según la página

                        content_element = await article_page.query_selector('div.article-content')
                        content_text = await content_element.inner_text() if content_element else "Contenido no disponible"

                    except Exception as e:
                        print(f"Error al cargar el artículo {i+1}: {e}")

                    await article_page.close()

                results.append({
                    'query': query,
                    'source': 'the balance money',
                    'title': 'headline_text',
                    'description': description_text,
                    'link': link,
                    'content': content_text
                })

        except Exception as e:
            print(f"Error durante la búsqueda de {query}: {e}")

        await browser.close()

    return results

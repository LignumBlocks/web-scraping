import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def run(playwright):
    # Lanzar el navegador (headless=False si quieres ver la ejecución)
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()

    # Crear una nueva página
    page = await context.new_page()

    # Navegar a la página de búsqueda de WSJ
    search_url = 'https://www.wsj.com/search'
    print(f"Accediendo a la URL: {search_url}")
    await page.goto(search_url)

    # Introducir la búsqueda usando la clase correcta
    search_term = "economía global"  # Cambia el término de búsqueda aquí
    print(f"Buscando por: {search_term}")
    
    # Escribir el término de búsqueda en el campo correcto
    await page.fill('.style--wsj-search-input--2m4pqsLm', search_term)

    # Enviar la búsqueda presionando Enter
    await page.press('.style--wsj-search-input--2m4pqsLm', 'Enter')

    # Esperar a que aparezcan los resultados
    await page.wait_for_selector('.WSJTheme--headlineText--He1ANr9C')

    # Extraer los titulares de los primeros 3 resultados
    headlines = await page.query_selector_all('.WSJTheme--headlineText--He1ANr9C')
    
    # Limitar a los primeros 3 resultados
    num_results = min(len(headlines), 3)
    print(f"Se encontraron {len(headlines)} resultados, mostrando los primeros {num_results}.")

    # Lista para almacenar los datos extraídos
    data = []

    for i in range(num_results):
        headline_element = headlines[i]
        headline_text = await headline_element.inner_text()
        link = await headline_element.eval_on_selector('a', 'a => a.href')  # Extraer el enlace
        print(f"Resultado {i+1}: Título: {headline_text}, Enlace: {link}")
        data.append({'title': headline_text, 'link': link})

    # Convertir los datos a un DataFrame y guardarlos en un CSV
    df = pd.DataFrame(data)
    df.to_csv('wsj_search_results.csv', index=False)
    print('Datos guardados en wsj_search_results.csv')

    # Cerrar el navegador
    await browser.close()

# Ejecutar Playwright de manera asíncrona
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

# Iniciar la ejecución
asyncio.run(main())

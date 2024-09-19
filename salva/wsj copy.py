import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def run(playwright):
    # Lanzar el navegador (headless=False si quieres ver la ejecución)
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()

    # Crear una nueva página
    page = await context.new_page()

    # Navegar a la URL de la galería de productos
    url = 'https://woodxel.com/high-end-wood-wall-art-gallery/'
    print(f"Accediendo a la URL: {url}")
    await page.goto(url)

    # Esperar a que los títulos de productos estén visibles
    await page.wait_for_selector('.woocommerce-loop-product__title')

    # Extraer todos los títulos de productos
    titles = await page.query_selector_all('.woocommerce-loop-product__title')

    # Lista para almacenar los datos extraídos
    data = []

    for i, title_element in enumerate(titles):
        title_text = await title_element.inner_text()  # Extraer el texto del título
        print(f"Producto {i+1}: {title_text}")
        data.append({'title': title_text})

    # Convertir los datos a un DataFrame y guardarlos en un CSV
    df = pd.DataFrame(data)
    df.to_csv('woodxel_product_titles.csv', index=False)
    print('Datos guardados en woodxel_product_titles.csv')

    # Cerrar el navegador
    await browser.close()

# Ejecutar Playwright de manera asíncrona
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

# Iniciar la ejecución
asyncio.run(main())

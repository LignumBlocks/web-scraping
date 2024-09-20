import pandas as pd
import asyncio
from scrapers.forbes_scraper import scrape_forbes
from scrapers.consumer_finance_scraper import scrape_consumer_finance
from scrapers.investopedia_scraper import scrape_investopedia
from scrapers.marketwatch_scraper import scrape_marketwatch
from scrapers.morningstar_scraper import scrape_morningstar
from scrapers.the_balance_money_scraper import scrape_the_balance_money
import os

# Lista de scrapers a activar (puedes incluir o eliminar fuentes según tu necesidad)
active_scrapers = [
    #'forbes',
    #'consumer finance',
    'investopedia',
    #'marketwatch',
    #'morningstar',
    #'the balance money'
]

# Función para guardar datos en CSV de forma incremental
def save_to_csv(data, file_name='results/scraping_results.csv'):
    df = pd.DataFrame(data)
    if not os.path.exists(file_name):
        # Si el archivo no existe, guardar con cabecera
        df.to_csv(file_name, mode='a', header=True, index=False)
    else:
        # Si el archivo ya existe, añadir sin cabecera
        df.to_csv(file_name, mode='a', header=False, index=False)

# Función principal para leer el CSV y realizar scraping
async def run_scraping():
    # Leer el archivo queries.csv
    df = pd.read_csv('queries.csv')

    # Iterar sobre cada fuente activa en el listado
    async with asyncio.TaskGroup() as tg:
        for scraper_name in active_scrapers:
            print(f"\n--- Ejecutando scraper para: {scraper_name.upper()} ---\n")

            # Iterar sobre cada fila en el archivo CSV (cada query list)
            for index, row in df.iterrows():
                query_list = eval(row['queries'])  # Si "queries" es un arreglo en formato de cadena, se convierte a una lista
                results = []

                # Ejecutar scrapers para la fuente actual
                if scraper_name == 'forbes':
                    for query in query_list:
                        results.extend(await tg.create_task(scrape_forbes(query)))

                elif scraper_name == 'consumer finance':
                    for query in query_list:
                        results.extend(await tg.create_task(scrape_consumer_finance(query)))

                elif scraper_name == 'investopedia':
                    for query in query_list:
                        results.extend(await tg.create_task(scrape_investopedia(query)))

                elif scraper_name == 'marketwatch':
                    for query in query_list:
                        results.extend(await tg.create_task(scrape_marketwatch(query)))

                elif scraper_name == 'morningstar':
                    for query in query_list:
                        results.extend(await tg.create_task(scrape_morningstar(query)))

                elif scraper_name == 'the balance money':
                    for query in query_list:
                        results.extend(await tg.create_task(scrape_the_balance_money(query)))

                # Guardar los resultados después de terminar con todas las queries de la fuente actual para esta fila del CSV
                if results:
                    save_to_csv(results)
                    print(f"Datos guardados en CSV para las queries de {scraper_name}: {query_list}")

# Función para ejecutar el scraping
asyncio.run(run_scraping())

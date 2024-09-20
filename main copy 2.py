import pandas as pd
import asyncio
import psycopg2
from dotenv import load_dotenv
import os
from scrapers.forbes_scraper import scrape_forbes
from scrapers.consumer_finance_scraper import scrape_consumer_finance
from scrapers.investopedia_scraper import scrape_investopedia
from scrapers.marketwatch_scraper import scrape_marketwatch
from scrapers.morningstar_scraper import scrape_morningstar
from scrapers.the_balance_money_scraper import scrape_the_balance_money

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Conectar a PostgreSQL
def connect_to_postgres():
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Guardar los resultados en PostgreSQL
def save_to_postgres(data, source, file_name):
    # Log para ver el contenido de 'data' antes de intentar guardarlo
    #print(f"Intentando guardar los siguientes datos:\nSource: {source}\nFile Name: {file_name}\nData: {data}\n")
    print(f"Intentando guardar los siguientes datos:\nSource: {source}\n")
    
    conn = connect_to_postgres()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO scraping_results (file_name, source, query, title, description, link, content)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        # Insertar cada resultado en la base de datos
        for result in data:
            # Log de cada registro
            #print(f"Inserting: Source: File Name: {file_name}, {result.get('source')},  Query: {result.get('query')}, Title: {result.get('title')}")
            cursor.execute(insert_query, (
                file_name,             # Nombre del archivo
                result.get('source'),  # Fuente del scraping (ej. marketwatch)                
                result.get('query'),   # Query ejecutada
                result.get('title'),   # Título del artículo o resultado
                result.get('description'),  # Descripción del artículo
                result.get('link'),    # Enlace al artículo original
                result.get('content')  # Contenido del artículo
            ))
        
        # Confirmar los cambios
        conn.commit()
        print(f"Datos guardados correctamente en la base de datos para {file_name}")

    except Exception as e:
        print(f"Error al guardar en PostgreSQL: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

# Función principal para leer el CSV y realizar scraping
async def run_scraping():
    # Leer el archivo queries.csv
    df = pd.read_csv('queries.csv')

    # Iterar sobre cada fuente activa en el listado
    async with asyncio.TaskGroup() as tg:
        for scraper_name in active_scrapers:
            print(f"\n--- Ejecutando scraper para: {scraper_name.upper()} ---\n")

            # Iterar sobre cada fila en el archivo CSV (cada query list y file_name)
            for index, row in df.iterrows():
                query_list = eval(row['queries'])  # Si "queries" es un arreglo en formato de cadena, se convierte a una lista
                file_name = row['file_name']  # Obtén el file_name asociado a la fila
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
                    # Agregar un log para ver los resultados que se obtuvieron antes de intentar guardarlos
                    #print(f"Resultados obtenidos para {scraper_name}, file_name: {file_name}: {results}")
                    save_to_postgres(results, scraper_name, file_name)
                    print(f"Datos guardados en la BD para las queries de {scraper_name} y file_name: {file_name}")

# Lista de scrapers a activar
active_scrapers = [
    #'forbes',
    #'consumer finance',
    #'investopedia',
    #'marketwatch',
    #'morningstar',
    'the balance money'
]

# Función para ejecutar el scraping
asyncio.run(run_scraping())

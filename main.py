import pandas as pd
import asyncio
import psycopg2
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from typing import List, Dict, Any
from scrapers.forbes_scraper import scrape_forbes
from scrapers.consumer_finance_scraper import scrape_consumer_finance
from scrapers.investopedia_scraper import scrape_investopedia
from scrapers.marketwatch_scraper import scrape_marketwatch
from scrapers.morningstar_scraper import scrape_morningstar
from scrapers.the_balance_money_scraper import scrape_the_balance_money

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Crear una instancia de FastAPI
app = FastAPI()

# Conectar a PostgreSQL
def connect_to_postgres():
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Guardar los resultados en PostgreSQL
def save_to_postgres(data, source, file_name):
    conn = connect_to_postgres()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO scraping_results (source, file_name, query, title, description, link, content)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        # Insertar cada resultado en la base de datos
        for result in data:
            cursor.execute(insert_query, (
                result.get('source'),  # Fuente del scraping (ej. marketwatch)
                file_name,             # Nombre del archivo
                result.get('query'),   # Query ejecutada
                result.get('title'),   # Título del artículo o resultado
                result.get('description'),  # Descripción del artículo
                result.get('link'),    # Enlace al artículo original
                result.get('content')  # Contenido del artículo
            ))
        
        # Confirmar los cambios
        conn.commit()

    except Exception as e:
        print(f"Error al guardar en PostgreSQL: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

# Función para ejecutar el scraping
async def run_scraping(data: List[Dict[str, Any]], active_scrapers: List[str]):
    results = []

    # Crear un TaskGroup para manejar los scrapers en paralelo
    async with asyncio.TaskGroup() as tg:
        for scraper_name in active_scrapers:
            print(f"\n--- Ejecutando scraper para: {scraper_name.upper()} ---\n")

            # Iterar sobre cada item en el JSON (queries, file_name, title, etc.)
            for item in data:
                query_list = item['queries']  # Lista de queries
                file_name = item['file_name']  # Nombre del archivo

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

                # Aquí agregaríamos el resto de los scrapers como marketwatch, etc.
                
                # Guardar resultados en la BD después de ejecutar todos los scrapers para esa fuente
                if results:
                    save_to_postgres(results, scraper_name, file_name)
    
    return results

@app.get("/")
async def read_root():
    return {"message": "Hola. API is up and running!"}

# Endpoint para recibir el JSON de fuentes y queries
@app.post("/scrape/")
async def scrape(
    sources: List[str],  # Lista de fuentes activas que el usuario pasa
    data: List[Dict[str, Any]]  # Lista de objetos JSON con file_name, title, brief_summary, y queries
):
    # Llamar a la función de scraping con las fuentes y la lista de queries
    results = await run_scraping(data, sources)

    # Devolver los resultados obtenidos
    return {"status": "success", "results": results}

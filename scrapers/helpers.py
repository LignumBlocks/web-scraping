import pandas as pd
import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from aiolimiter import AsyncLimiter

# Rate limiter: 5 requests por minuto
limiter = AsyncLimiter(5, 60)

# Retry logic: reintentar 3 veces con 2 segundos de espera entre intentos para funciones asíncronas
def async_retry(func):
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper

# Función para obtener proxies (puedes personalizar esta función para obtener proxies dinámicos)
def get_proxies():
    # Aquí puedes implementar una lista de proxies si tienes una fuente
    return None  # Si no usas proxy, devuelve None

# Guardar resultados en CSV
def save_to_csv(data, file_name):
    df = pd.DataFrame(data)
    df.to_csv(file_name, mode='a', header=not pd.io.common.file_exists(file_name), index=False)
    logging.info(f"Datos guardados en {file_name}")

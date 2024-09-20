import psycopg2
import os
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

# Función para conectarse a PostgreSQL
def connect_to_postgres():
    try:
        # Obtener la URL de la base de datos desde las variables de entorno
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        # Intentar establecer una conexión
        conn = psycopg2.connect(DATABASE_URL)
        print("Conexión exitosa a PostgreSQL.")
        
        return conn

    except Exception as e:
        print(f"Error al conectarse a la base de datos: {e}")
        return None

# Función para probar la conexión ejecutando una consulta
def test_connection():
    conn = connect_to_postgres()

    if conn:
        try:
            # Crear un cursor para ejecutar comandos SQL
            cursor = conn.cursor()

            # Ejecutar una simple consulta para verificar la conexión
            cursor.execute("SELECT version();")

            # Obtener el resultado de la consulta
            record = cursor.fetchone()

            print(f"Versión de PostgreSQL: {record}")

            # Cerrar el cursor y la conexión
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")

# Ejecutar la función de prueba
if __name__ == "__main__":
    test_connection()

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

dotenv_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(dotenv_dir, '.env')

# Cargar el archivo .env desde la ruta especificada
loaded_env = load_dotenv(dotenv_path=dotenv_path)

if loaded_env:
    print(f"Archivo .env cargado exitosamente desde: {dotenv_path}")
else:
    print(f"ADVERTENCIA: No se pudo cargar el archivo .env desde: {dotenv_path}. Usando valores predeterminados o variables de entorno del sistema.")

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '192.168.1.89'),
    'database': os.getenv('DB_NAME', 'pcparts'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', ''),
    'collation': 'utf8mb4_general_ci'
}

# Verificar que las variables de entorno esenciales estén cargadas
# Esta verificación ahora reflejará mejor si las variables del .env se cargaron o no.
if not DB_CONFIG['user'] or not DB_CONFIG['password'] or DB_CONFIG['user'] == 'root': # Añadida comprobación extra por si 'root' es el default no deseado
    print("INFO: Verificando variables de entorno para la BD...")
    if not os.getenv('DB_USER') or not os.getenv('DB_PASS'):
        print("ERROR: Las variables de entorno DB_USER y/o DB_PASS no están definidas o no se cargaron correctamente desde el .env.")
        print(f"Intentando cargar DB_USER: {os.getenv('DB_USER')}, DB_PASS: {'*' * len(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else None}")


def create_db_connection():
    """Crea una conexión a la base de datos."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Error '{e}' al conectar a MariaDB desde create_db_connection")
        # Podrías relanzar la excepción o manejarla de forma más específica si es necesario
    return connection
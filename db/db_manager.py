import logging
import psycopg2
from config.config import app_env

logger = logging.getLogger("uvicorn")

def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos usando psycopg2.
    """
    try:
        conn = psycopg2.connect(app_env.DB_URL)
        logger.info("Conexión a la base de datos establecida correctamente.")
        return conn
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        raise e
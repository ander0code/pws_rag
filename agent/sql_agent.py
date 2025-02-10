import asyncio
import logging
import psycopg2
import psycopg2.extras
from agent.agent import llm
# from config.config import app_env  

import re
from db.db_manager import get_db_connection


logger = logging.getLogger("uvicorn")

# 🔹 **Ejecutar una consulta SQL con psycopg2**
def execute_sql_query(sql_query: str, params=None):
    """
    Ejecuta una consulta SQL en PostgreSQL y devuelve los resultados como lista de diccionarios.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        logger.debug(f"Ejecutando SQL: {sql_query} con parámetros: {params}")

        cursor.execute(sql_query, params or ())
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]

        logger.info(f"Consulta SQL ejecutada con éxito, filas retornadas: {len(result)}")

        cursor.close()
        conn.close()
        return result
    except psycopg2.errors.UndefinedTable:
        logger.error("Error: La tabla no existe en la base de datos.")
        return []
    except Exception as e:
        logger.error(f"Error ejecutando SQL: {e}")
        return 

def clean_sql_query(query: str) -> str:
    """
    Elimina los delimitadores Markdown y espacios innecesarios de la consulta generada.
    """
    if query.startswith("```"):
        lines = query.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        query = "\n".join(lines).strip()
    return query

async def generate_sql_query(user_input: str) -> str:
    db_schema = """
        -- Tabla ProjectUnit (Unidades de vivienda)
        CREATE TABLE ProjectUnit (
            id VARCHAR(25) PRIMARY KEY,
            projectId VARCHAR(25) NOT NULL,
            name VARCHAR(50),
            type VARCHAR(50),  -- (Ej: 'departamento', 'casa')
            price BIGINT,
            area VARCHAR(50),
            layout VARCHAR(50),
            floor INTEGER,
            typologyId VARCHAR(25), -- Relación con Typology
            commercialStatusId VARCHAR(25), -- Relación con ColCommercialStatus
            deletedAt TIMESTAMP NULL
        );

        -- Tabla Project (Proyectos Inmobiliarios)
        CREATE TABLE Project (
            id VARCHAR(25) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            address VARCHAR(100),
            districtId VARCHAR(25) NOT NULL, -- Relación con ColDistrict
            countryId VARCHAR(25) NOT NULL -- Relación con ColCountry
        );

        -- Tabla ColDistrict (Distritos)
        CREATE TABLE ColDistrict (
            id VARCHAR(25) PRIMARY KEY,
            description VARCHAR(100) NOT NULL
        );

        -- Tabla Typology (Tipos de vivienda)
        CREATE TABLE Typology (
            id VARCHAR(25) PRIMARY KEY,
            code VARCHAR(50),
            bedroomsCount INTEGER,
            bathroomsCount INTEGER,
            projectId VARCHAR(25) NOT NULL -- Relación con Project
        );

        -- Tabla ColCommercialStatus (Estado Comercial)
        CREATE TABLE ColCommercialStatus (
            id VARCHAR(25) PRIMARY KEY,
            description VARCHAR(100) NOT NULL -- (Ej: 'selling', 'reserved', 'delivered')
        );
        """
        
    prompt = (
        f"Dado el siguiente esquema de base de datos:\n{db_schema}\n\n"
        f"Y la consulta del usuario: '{user_input}', genera una consulta SQL en texto plano para obtener propiedades disponibles "
        "de la tabla \"ProjectUnit\". Relaciona esta tabla con \"Project\" para obtener el nombre del proyecto y con \"ColDistrict\" "
        "para filtrar por ubicación si se menciona un distrito en la consulta.\n\n"

        "Aplica las siguientes reglas al construir la consulta:\n"
        "- que respete el nombre de las columnas y tablas del esquema.\n"
        "- Si el usuario menciona un precio, filtra propiedades en un rango de ±5,000 unidades monetarias.\n"
        "- Si menciona cantidad de dormitorios o baños, usa los valores desde \"Typology\".\n"
        "- Si menciona 'departamento' o 'casa', filtra por el campo 'type' en \"ProjectUnit\".\n"
        "- Si especifica estado comercial (ej. 'en venta', 'entregado'), filtra usando \"ColCommercialStatus\".\n"
        "- Usa nombres de tablas y columnas exactamente como están en el esquema, con comillas dobles.\n"
        "- La consulta debe ser compatible con PostgreSQL y no incluir comentarios ni texto adicional.\n\n"

        "**No agregues prefijos como 'AI:', 'Bot:' o 'Respuesta:'. Solo devuelve la consulta SQL en texto plano.**\n\n"

        "Si no es posible generar una consulta válida, responde exactamente 'None'."
    )
    logger.debug(f"Prompt para generar consulta SQL: {prompt}")
    sql_response = await asyncio.to_thread(llm.invoke, prompt)
    try:
        if hasattr(sql_response, "content"):
            raw_sql = sql_response.content.strip()
        else:
            raw_sql = "None"
        raw_sql = clean_sql_query(raw_sql)
        print(f"Consulta SQL generada por LLM: {raw_sql}")
    except Exception as e:
        logger.error(f"Error parseando respuesta del LLM para consulta SQL: {e}")
        raw_sql = "None"
    return raw_sql


logger = logging.getLogger("uvicorn")

def is_db_query(user_input: str) -> bool:
    """Verifica si el input del usuario tiene palabras clave relacionadas a departamentos/viviendas."""
    keywords = ["departamento", "vivienda", "casa"]
    return any(word in user_input.lower() for word in keywords)

def is_consulta_especifica(user_input: str) -> bool:
    """Valida patrones que indican una consulta específica."""
    patrones = [r"mismo precio", r"surco", r"precio de", r"detalles"]
    return any(re.search(p, user_input.lower()) for p in patrones)

def get_unit_details(user_input: str) -> list:
    """
    Genera y ejecuta una consulta SQL basada en el input del usuario para obtener información de propiedades.
    """
    # 🔹 Generar la consulta SQL desde el LLM
    sql_query = asyncio.run(generate_sql_query(user_input))
    
    # 🔹 Si la consulta generada es "None", retornar mensaje de error
    if not sql_query or sql_query.lower() == "none":
        logger.warning("El LLM no generó una consulta SQL válida.")
        return "No se pudo generar una consulta para esta solicitud."

    # 🔹 Ejecutar la consulta generada dinámicamente
    result = execute_sql_query(sql_query)
    
    # 🔹 Retornar los resultados obtenidos o un mensaje si no hay coincidencias
    if result:
        return result
    else:
        return "No se encontraron departamentos que coincidan con tu solicitud."


def build_prompt_with_db_data(unit) -> str:
    """
    Construye un mensaje con la información de la unidad para incluirlo en el prompt del RAG.
    """
    if not unit:
        return "No se encontró información para el departamento solicitado."

    return (
        f"Detalles del departamento:\n"
        f"- Proyecto: {unit['project_name']}\n"
        f"- Nombre: {unit['name']}\n"
        f"- Tipo: {unit['type']}\n"
        f"- Precio: {unit['price']} soles\n"
        f"- Área: {unit['area']} m²\n"
        f"- Habitaciones: {unit['bedroomsCount']} \n"
        f"- Baños: {unit['bathroomsCount']} \n"
        f"- Piso: {unit['floor']}\n"
        f"- Distribución: {unit['layout']}\n"
        f"- Estado: {unit['commercial_status']}\n"
        f"- Ubicacion: {unit['district']}\n"
    )

def process_department_query(user_input: str) -> str:

    match = re.search(r'(\bdep-\d+\b)', user_input)
    unit_id = match.group(1) if match else None

    if not unit_id:
        return "No se pudo identificar un departamento específico en tu mensaje. ¿Podrías proporcionar más detalles?"

    logger.debug(f"Procesando consulta departamental para unit_id: {unit_id}")
    unit_info = get_unit_details(unit_id)

    if not unit_info:
        return "No se encontró información para el departamento solicitado."

    return build_prompt_with_db_data(unit_info)
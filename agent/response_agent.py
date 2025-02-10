import logging
from agent.sql_agent import is_db_query, is_consulta_especifica, process_department_query
from agent.sql_agent import generate_sql_query, execute_sql_query
from agent.embending_agent import conversational_rag_chain

logger = logging.getLogger("uvicorn")

async def handle_user_question(user_input: str, session_id: str, company_id: str) -> dict:
    """
    Procesa el input del usuario, generando (si es necesario) una consulta SQL a través del LLM y combinando
    la respuesta con los datos obtenidos de la BD.
    """
    db_prompt = ""
    if is_db_query(user_input):
        logger.info("Se detectó consulta sobre departamentos/viviendas.")
        if is_consulta_especifica(user_input):
            logger.info("Consulta específica. Generando consulta SQL con LLM...")
            sql_query = await generate_sql_query(user_input)
            logger.debug(f"SQL query generada: {sql_query}")
            if sql_query and sql_query.lower() != "none":
                query_result = execute_sql_query(sql_query)

                if query_result:
                    # Si hay resultados en SQL, formatear la respuesta
                    properties = "\n".join([
                        f"- {row['project_name']} ({row['type']}, {row['area']} m²) - {row['price']} soles"
                        for row in query_result
                    ])
                    db_prompt = f"Aquí tienes opciones disponibles:\n{properties}.\n ¿Te gustaría más detalles?"
                else:
                    db_prompt = "Lo siento, actualmente no hay departamentos disponibles en Surco o el Centro de Lima. ¿Te gustaría buscar en otra ubicación o ajustar tu criterio?"
            else:
                logger.warning("LLM no generó una consulta SQL válida.")
        else:
            logger.info("Consulta general detectada. Procesando consulta departamental.")
            db_prompt = process_department_query(user_input)
    
    final_prompt = f"{db_prompt}\n\n{user_input}"
    logger.debug(f"Prompt final para RAG:\n{final_prompt}")
    
    rag_response = await conversational_rag_chain(company_id, session_id, final_prompt)
    
    if "AI:" in rag_response.get("message", ""):
        rag_response["message"] = rag_response["message"].replace("AI:", "").strip()

    return {
        "query": user_input,
        "message": rag_response.get("message", "No se pudo generar una respuesta")
    }

async def get_response_agent(user_input: str, session_id: str, company_id: str, filter_: dict = {}) -> dict:
    """
    Función principal que orquesta el flujo final.
    Decide si la consulta requiere acceder a la BD o se puede responder directamente vía RAG.
    """
    logger.info("Iniciando flujo en response_agent.")
    try:
        if is_db_query(user_input):
            logger.info("Se detectó consulta DB, invocando handle_user_question.")
            response = await handle_user_question(user_input, session_id, company_id)
        else:
            response = await conversational_rag_chain(company_id, session_id, user_input)
            logger.debug(f"Resultado de conversational_rag_chain: {response}")
            if response is None:
                raise ValueError("El resultado de conversational_rag_chain es None.")

        # 🔹 **Eliminar "AI:" si aparece en la respuesta**
        if "AI:" in response.get("message", ""):
            response["message"] = response["message"].replace("AI:", "").strip()

        return response

    except Exception as e:
        logger.error(f"Error en get_response_agent: {e}")
        return {"query": user_input, "message": "Error procesando tu solicitud"}
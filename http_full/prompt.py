# ===============================================
# DESCRIPCIONES DE HERRAMIENTAS (JSON)
# ===============================================
TOOL_DESCRIPTIONS = {
    "sumar": {"description": "Suma dos números", "examples": ["suma 5 y 3"]},
    "multiplicar": {"description": "Multiplica dos números", "examples": ["multiplica 4 por 5"]},
    "getUserInfo": {"description": "Obtiene información de un usuario", "examples": ["usuario 123"]},
    "getWeather": {"description": "Obtiene el clima de una ubicación", "examples": ["clima en Madrid"]},
}

ORCHESTRATOR_PROMPT = """Eres un orquestador inteligente.

Herramientas disponibles:
{tool_descriptions}
"""

#!/usr/bin/env python3
"""
Servidor MCP con Orquestador Completo
Punto 3: Todo el orquestador y las herramientas en el servidor MCP
"""

import os
from mcp.server.fastmcp import FastMCP
from typing import Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Cargar variables de entorno
load_dotenv()

# Crear servidor MCP
mcp_server = FastMCP("OrchestratorServer")

# ===============================================
# ESQUEMAS PYDANTIC PARA HERRAMIENTAS INTERNAS
# ===============================================
class SumarInternoSchema(BaseModel):
    a: float = Field(description="Primer número a sumar")
    b: float = Field(description="Segundo número a sumar")

class MultiplicarInternoSchema(BaseModel):
    a: float = Field(description="Primer número a multiplicar")
    b: float = Field(description="Segundo número a multiplicar")

class GetUserInfoInternoSchema(BaseModel):
    user_id: str = Field(description="ID del usuario a buscar")

class GetWeatherInternoSchema(BaseModel):
    location: str = Field(description="Ubicación para consultar el clima")

# ===============================================
# HERRAMIENTAS INTERNAS (CON DESCRIPTION EN DECORADOR)
# ===============================================
@tool(args_schema=SumarInternoSchema, description="Suma dos números enteros o decimales")
def sumar_interno(a: float, b: float) -> float:
    return a + b

@tool(args_schema=MultiplicarInternoSchema, description="Multiplica dos números enteros o decimales")
def multiplicar_interno(a: float, b: float) -> float:
    return a * b

@tool(args_schema=GetUserInfoInternoSchema, description="Obtiene información de un usuario por su ID")
def getUserInfo_interno(user_id: str) -> Dict:
    users_db = {
        "123": {"name": "Juan Pérez", "email": "juan@example.com", "active": True},
        "456": {"name": "María García", "email": "maria@example.com", "active": False},
    }
    return users_db.get(user_id, {"error": "Usuario no encontrado"})

@tool(args_schema=GetWeatherInternoSchema, description="Obtiene el clima de una ubicación")
def getWeather_interno(location: str) -> Dict:
    weather_db = {
        "nueva york": {"temp": "22°C", "condition": "Soleado"},
        "madrid": {"temp": "18°C", "condition": "Nublado"},
        "londres": {"temp": "15°C", "condition": "Lluvioso"},
    }
    return weather_db.get(location.lower(), {"error": "Ubicación no encontrada"})

# ===============================================
# DESCRIPCIONES Y PROMPT
# ===============================================
TOOL_DESCRIPTIONS = {
    "sumar_interno": {"description": "Suma dos números", "examples": ["suma 5 y 3"]},
    "multiplicar_interno": {"description": "Multiplica dos números", "examples": ["multiplica 4 por 5"]},
    "getUserInfo_interno": {"description": "Información de usuario", "examples": ["usuario 123"]},
    "getWeather_interno": {"description": "Clima de ubicación", "examples": ["clima en Madrid"]},
}

ORCHESTRATOR_PROMPT = """Eres un asistente orquestador inteligente.

Herramientas disponibles:
{tool_descriptions}

Analiza el mensaje y ejecuta la herramienta apropiada."""

# ===============================================
# ORQUESTADOR EN SERVIDOR (ASÍNCRONO)
# ===============================================
class ServerOrchestrator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tools = [sumar_interno, multiplicar_interno, getUserInfo_interno, getWeather_interno]
        
        tool_descriptions_str = "\n".join([
            f"- {name}: {desc['description']}"
            for name, desc in TOOL_DESCRIPTIONS.items()
        ])
        
        prompt_template = ORCHESTRATOR_PROMPT.format(tool_descriptions=tool_descriptions_str)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_template),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def process(self, message: str) -> str:
        """Procesa mensaje con orquestador interno - ASÍNCRONO con ainvoke"""
        response = await self.agent_executor.ainvoke({"input": message})
        return response["output"]

# Instancia global del orquestador
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ServerOrchestrator()
    return _orchestrator

# ===============================================
# HERRAMIENTA MCP EXPUESTA (SIN DOCSTRING)
# ===============================================
@mcp_server.tool()
async def process_message(message: str) -> str:
    orchestrator = get_orchestrator()
    result = await orchestrator.process(message)
    return result

# ===============================================
# EJECUTAR SERVIDOR
# ===============================================
if __name__ == "__main__":
    print("🚀 Iniciando servidor MCP con Orquestador completo...")
    print("🧠 El orquestador y las herramientas están en el servidor")
    mcp_server.run(transport="stdio")


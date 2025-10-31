#!/usr/bin/env python3
"""
Servidor MCP con Orquestador Completo HTTP
Punto Full HTTP: Orquestador y herramientas en servidor MCP HTTP
"""
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Dict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
import uvicorn

from .prompt import TOOL_DESCRIPTIONS, ORCHESTRATOR_PROMPT

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

# Crear servidor MCP HTTP
mcp_server = FastMCP("OrchestratorServerHTTP")
app = mcp_server.sse_app()

# ===============================================
# ESQUEMAS PYDANTIC PARA HERRAMIENTAS INTERNAS
# ===============================================
class SumarSchema(BaseModel):
    a: float = Field(description="Primer número a sumar")
    b: float = Field(description="Segundo número a sumar")

class MultiplicarSchema(BaseModel):
    a: float = Field(description="Primer número a multiplicar")
    b: float = Field(description="Segundo número a multiplicar")

class GetUserSchema(BaseModel):
    user_id: str = Field(description="ID del usuario a buscar")

class GetWeatherSchema(BaseModel):
    location: str = Field(description="Ubicación para consultar el clima")

# ===============================================
# HERRAMIENTAS EN EL SERVIDOR
# ===============================================
@tool(args_schema=SumarSchema, description="Suma dos números")
def sumar(a: float, b: float) -> float:
    return a + b

@tool(args_schema=MultiplicarSchema, description="Multiplica dos números")
def multiplicar(a: float, b: float) -> float:
    return a * b

@tool(args_schema=GetUserSchema, description="Obtiene información de un usuario")
def getUserInfo(user_id: str) -> Dict:
    users = {"123": {"name": "Juan Pérez", "email": "juan@example.com"}}
    return users.get(user_id, {"error": "Usuario no encontrado"})

@tool(args_schema=GetWeatherSchema, description="Obtiene el clima de una ubicación")
def getWeather(location: str) -> Dict:
    weather_db = {"madrid": {"temp": "18°C", "condition": "Nublado"}}
    return weather_db.get(location.lower(), {"error": "Ubicación no encontrada"})

# ===============================================
# ORQUESTADOR INTERNO
# ===============================================
class ServerOrchestratorHTTP:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
        tools = [sumar, multiplicar, getUserInfo, getWeather]
        desc = "\n".join([f"- {n}: {d['description']}" for n, d in TOOL_DESCRIPTIONS.items()])
        prompt = ChatPromptTemplate.from_messages([
            ("system", ORCHESTRATOR_PROMPT.format(tool_descriptions=desc)),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        self.executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    async def process(self, message: str) -> str:
        result = await self.executor.ainvoke({"input": message})
        return result["output"]

_orchestrator = ServerOrchestratorHTTP()

# ===============================================
# ENDPOINT MCP: process_message expuesto como tool
# ===============================================
@mcp_server.tool()
async def process_message(message: str) -> str:
    return await _orchestrator.process(message)

# ===============================================
# EJECUTAR SERVIDOR
# ===============================================
if __name__ == "__main__":
    print("🚀 Iniciando Full HTTP MCP Server...")
    print("📡 SSE en http://0.0.0.0:8001/sse")
    uvicorn.run(app, host="0.0.0.0", port=8001)

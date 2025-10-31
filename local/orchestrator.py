#!/usr/bin/env python3
""" Orquestador.

Todas las clases, herramientas, schemas y lógica compartida
"""

import os
import sys
# Asegurar que prompt.py se importe desde esta carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typing import Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from mcp_examples.local.prompt import TOOL_DESCRIPTIONS, ORCHESTRATOR_PROMPT

# Cargar variables de entorno
load_dotenv()

# ===============================================
# ESQUEMAS PYDANTIC
# ===============================================
class SumarSchema(BaseModel):
    a: float = Field(description="Primer número a sumar")
    b: float = Field(description="Segundo número a sumar")

class MultiplicarSchema(BaseModel):
    a: float = Field(description="Primer número a multiplicar")
    b: float = Field(description="Segundo número a multiplicar")

class GetUserInfoSchema(BaseModel):
    user_id: str = Field(description="ID del usuario a buscar")

class GetWeatherSchema(BaseModel):
    location: str = Field(description="Ubicación para consultar el clima")

# ===============================================
# HERRAMIENTAS
# ===============================================
@tool(args_schema=SumarSchema, description="Suma dos números enteros o decimales")
def sumar(a: float, b: float) -> float:
    return a + b

@tool(args_schema=MultiplicarSchema, description="Multiplica dos números enteros o decimales")
def multiplicar(a: float, b: float) -> float:
    return a * b

@tool(args_schema=GetUserInfoSchema, description="Obtiene información de un usuario por su ID")
def getUserInfo(user_id: str) -> Dict:
    users_db = {
        "123": {"name": "Juan Pérez", "email": "juan@example.com", "active": True},
        "456": {"name": "María García", "email": "maria@example.com", "active": False},
    }
    return users_db.get(user_id, {"error": "Usuario no encontrado"})

@tool(args_schema=GetWeatherSchema, description="Obtiene el clima de una ubicación")
def getWeather(location: str) -> Dict:
    weather_db = {
        "nueva york": {"temp": "22°C", "condition": "Soleado"},
        "madrid": {"temp": "18°C", "condition": "Nublado"},
        "londres": {"temp": "15°C", "condition": "Lluvioso"},
    }
    return weather_db.get(location.lower(), {"error": "Ubicación no encontrada"})

# ===============================================
# CLASE: ORQUESTADOR LOCAL
# ===============================================
class LocalOrchestrator:
    """Orquestador Local.

    """
        
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tools = [sumar, multiplicar, getUserInfo, getWeather]
        
        tool_descriptions_str = "\n".join([
            f"- {name}: {desc['description']} | Ejemplos: {', '.join(desc['examples'])}"
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
    
    def process_message(self, message: str) -> str:
        """Procesa un mensaje - SÍNCRONO"""
        response = self.agent_executor.invoke({"input": message})
        return response["output"]
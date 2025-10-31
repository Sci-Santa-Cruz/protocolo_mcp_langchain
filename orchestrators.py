#!/usr/bin/env python3
"""
Orquestadores y Código Común
Todas las clases, herramientas, schemas y lógica compartida
"""

import os
from typing import Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Cargar variables de entorno
load_dotenv()

# ===============================================
# DESCRIPCIONES DE HERRAMIENTAS (JSON)
# ===============================================
TOOL_DESCRIPTIONS = {
    "sumar": {
        "name": "sumar",
        "description": "Suma dos números enteros o decimales",
        "examples": ["suma 5 y 3", "cuanto es 10 + 20"]
    },
    "multiplicar": {
        "name": "multiplicar",
        "description": "Multiplica dos números enteros o decimales",
        "examples": ["multiplica 4 por 5", "cuanto es 7 x 8"]
    },
    "getUserInfo": {
        "name": "getUserInfo",
        "description": "Obtiene información de un usuario por su ID",
        "examples": ["info del usuario 123", "datos de user456"]
    },
    "getWeather": {
        "name": "getWeather",
        "description": "Obtiene el clima de una ubicación",
        "examples": ["clima en Nueva York", "temperatura en Madrid"]
    }
}

ORCHESTRATOR_PROMPT = """Eres un asistente orquestador inteligente.

Tu trabajo es analizar el mensaje del usuario y decidir qué herramienta ejecutar.

Herramientas disponibles:
{tool_descriptions}

Analiza el mensaje y ejecuta la herramienta apropiada."""

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
    """Orquestador con herramientas locales (síncrono)"""
    
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

# ===============================================
# CLASE: ORQUESTADOR CON CLIENTE MCP (STDIO)
# ===============================================
class MCPOrchestrator:
    """Orquestador en cliente, herramientas en servidor MCP stdio (asíncrono)"""
    
    def __init__(self, server_path="tools_server.py"):
        # Diagnóstico de entorno
        print(f"[MCPOrchestrator.__init__] cwd={os.getcwd()}")
        print(f"[MCPOrchestrator.__init__] server_path (input)={server_path}")

        # Normalizar ruta absoluta al servidor
        if not os.path.isabs(server_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # server_path relativo a stdio_tools
            # __file__ apunta a mcp_examples/orchestrators.py; stdio_tools está al mismo nivel
            server_path = os.path.join(os.path.dirname(base_dir), "stdio_tools", server_path)
        self.server_path = server_path
        print(f"[MCPOrchestrator.__init__] server_path (abs)={self.server_path}")
        print(f"[MCPOrchestrator.__init__] server exists={os.path.exists(self.server_path)}")

        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.client = MultiServerMCPClient({
            "tools": {
                "transport": "stdio",
                "command": "python",
                "args": [self.server_path]
            }
        })
        self.initialized = False
    
    async def initialize(self):
        """Inicializa el cliente MCP"""
        if self.initialized:
            return
            
        print("[MCPOrchestrator.initialize] solicitando herramientas al servidor...")
        try:
            self.tools = await self.client.get_tools()
        except Exception as e:
            print(f"[MCPOrchestrator.initialize] ERROR get_tools: {e}")
            raise
        
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
        
        self.initialized = True
    
    async def process_message(self, message: str) -> str:
        """Procesa un mensaje - ASÍNCRONO"""
        if not self.initialized:
            await self.initialize()
        
        response = await self.agent_executor.ainvoke({"input": message})
        return response["output"]

# ===============================================
# CLASE: ORQUESTADOR CON CLIENTE MCP (HTTP)
# ===============================================
class MCPOrchestratorHTTP:
    """Orquestador en cliente, herramientas en servidor MCP HTTP (asíncrono)"""
    
    def __init__(self, server_url: str = "http://localhost:8000/sse"):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.client = MultiServerMCPClient({
            "tools": {
                "transport": "sse",
                "url": server_url,
            }
        })
        self.initialized = False
    
    async def initialize(self):
        """Inicializa el cliente MCP HTTP"""
        if self.initialized:
            return
            
        self.tools = await self.client.get_tools()
        
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
        
        self.initialized = True
    
    async def process_message(self, message: str) -> str:
        """Procesa un mensaje - ASÍNCRONO"""
        if not self.initialized:
            await self.initialize()
        
        response = await self.agent_executor.ainvoke({"input": message})
        return response["output"]

# ===============================================
# CLASE: CLIENTE MCP SIMPLE (STDIO)
# ===============================================
class SimpleMCPClient:
    """Cliente simple que se conecta a servidor con orquestador completo (stdio)"""
    
    def __init__(self):
        self.client = MultiServerMCPClient({
            "orchestrator": {
                "transport": "stdio",
                "command": "python",
                "args": ["orchestrator_server.py"]
            }
        })
        self.initialized = False
        self.process_tool = None
    
    async def initialize(self):
        """Inicializa el cliente"""
        if self.initialized:
            return
        
        tools = await self.client.get_tools()
        self.process_tool = tools[0]
        self.initialized = True
    
    async def send_message(self, message: str) -> str:
        """Envía mensaje al servidor"""
        if not self.initialized:
            await self.initialize()
        
        response = await self.process_tool.ainvoke({"message": message})
        return response

# ===============================================
# CLASE: CLIENTE MCP SIMPLE (HTTP)
# ===============================================
class SimpleMCPClientHTTP:
    """Cliente simple que se conecta a servidor HTTP con orquestador completo"""
    
    def __init__(self, server_url: str = "http://localhost:8001/sse"):
        self.client = MultiServerMCPClient({
            "orchestrator": {
                "transport": "sse",
                "url": server_url,
            }
        })
        self.initialized = False
        self.process_tool = None
    
    async def initialize(self):
        """Inicializa el cliente HTTP"""
        if self.initialized:
            return
        
        tools = await self.client.get_tools()
        self.process_tool = tools[0]
        self.initialized = True
    
    async def send_message(self, message: str) -> str:
        """Envía mensaje al servidor HTTP"""
        if not self.initialized:
            await self.initialize()
        
        response = await self.process_tool.ainvoke({"message": message})
        return response


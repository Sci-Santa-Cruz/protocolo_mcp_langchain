#!/usr/bin/env python3
"""
Servidor MCP con Herramientas
Punto 2: Las herramientas corren en el servidor MCP
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict

# Crear servidor MCP
mcp_server = FastMCP("ToolsServer")

# ===============================================
# HERRAMIENTAS EN SERVIDOR MCP (SIN DOCSTRING)
# ===============================================
@mcp_server.tool()
def sumar(a: float, b: float) -> float:
    return a + b

@mcp_server.tool()
def multiplicar(a: float, b: float) -> float:
    return a * b

@mcp_server.tool()
def getUserInfo(user_id: str) -> Dict:
    users_db = {
        "123": {"name": "Juan Pérez", "email": "juan@example.com", "active": True},
        "456": {"name": "María García", "email": "maria@example.com", "active": False},
    }
    return users_db.get(user_id, {"error": "Usuario no encontrado"})

@mcp_server.tool()
def getWeather(location: str) -> Dict:
    weather_db = {
        "nueva york": {"temp": "22°C", "condition": "Soleado"},
        "madrid": {"temp": "18°C", "condition": "Nublado"},
        "londres": {"temp": "15°C", "condition": "Lluvioso"},
    }
    return weather_db.get(location.lower(), {"error": "Ubicación no encontrada"})

# ===============================================
# EJECUTAR SERVIDOR
# ===============================================
if __name__ == "__main__":
    print("🚀 Iniciando servidor MCP en modo stdio...")
    mcp_server.run(transport="stdio")


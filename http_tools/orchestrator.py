#!/usr/bin/env python3
"""
Servidor MCP con Herramientas - HTTP Remoto
Punto 2 (Remoto): Las herramientas corren en un servidor HTTP accesible remotamente
"""
import uvicorn  # servidor ASGI para SSE
from mcp.server.fastmcp import FastMCP
from typing import Dict

# Crear servidor MCP
mcp_server = FastMCP("ToolsServerHTTP")  # contiene sse_app con rutas SSE
# Exponer ASGI app en variable de módulo para uvicorn
app = mcp_server.sse_app()

# ===============================================
# HERRAMIENTAS EN SERVIDOR MCP
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
# EJECUTAR SERVIDOR HTTP
# ===============================================
if __name__ == "__main__":
    print("🚀 Iniciando servidor MCP SSE con Uvicorn...")
    print("📡 Servidor accesible en: http://0.0.0.0:8000/sse")
    # Ejecutar la app SSE expuesta por FastMCP en /sse
    uvicorn.run(
        mcp_server.sse_app(),
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )

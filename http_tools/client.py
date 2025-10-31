#!/usr/bin/env python3
"""
Interfaz Gradio para Orquestador con Cliente MCP HTTP
Punto 2 (Remoto): UI para orquestador en cliente, herramientas en servidor MCP HTTP
"""

import asyncio
import gradio as gr
from typing import List, Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..orchestrators import MCPOrchestratorHTTP
from dotenv import load_dotenv

# Cargar variables de entorno (para modo dummy si se desea)
load_dotenv()

# Modo diagnóstico HTTP
DUMMY_HTTP = os.getenv("MCP_DUMMY_HTTP") == "1"

# ===============================================
# CONFIGURACIÓN
# ===============================================
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000/sse")  # Usar variable de entorno para conectar dentro de Docker

# ===============================================
# INSTANCIA GLOBAL DEL ORQUESTADOR
# ===============================================
orchestrator = MCPOrchestratorHTTP(server_url=SERVER_URL)

# ===============================================
# FUNCIONES PARA GRADIO
# ===============================================
async def process_chat_async(message: str, history: List[List[str]]) -> Tuple[List[List[str]], str]:
    """Procesa un mensaje de forma asíncrona con timeout y logs"""
    if not message.strip():
        return history, ""
    try:
        print(f"[HTTP] Recibido mensaje: {message}")
        if DUMMY_HTTP:
            response = f"[DUMMY_HTTP] Echo: {message}"
        else:
            # timeout para evitar spinner infinito
            response = await asyncio.wait_for(
                orchestrator.process_message(message),
                timeout=25
            )
        print("[HTTP] Respuesta lista")
        history.append((message, response))
        return history, ""
    except asyncio.TimeoutError:
        error_msg = "❌ Timeout: el servidor HTTP no respondió a tiempo (25s)."
        print("[HTTP] Timeout esperando respuesta")
        history.append((message, error_msg))
        return history, ""
    except Exception as e:
        # Capturar detalles de la excepción
        import traceback
        tb = traceback.format_exc()
        # Mostrar mensaje de error con traceback en la GUI
        error_msg = (
            f"❌ Error: {str(e)}\n\n"
            f"Detalles técnicos:\n```\n{tb}\n```"
        )
        history.append((message, error_msg))
        return history, ""

def process_chat(message: str, history: List[List[str]]) -> Tuple[List[List[str]], str]:
    """Wrapper síncrono para Gradio"""
    return asyncio.run(process_chat_async(message, history))

def clear_chat():
    """Limpia el historial del chat"""
    return [], ""

# ===============================================
# INTERFAZ GRADIO
# ===============================================

def create_gradio_interface():
    """Crea la interfaz de Gradio"""
    with gr.Blocks(
        title="🌐 Orquestador con Servidor MCP HTTP",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1000px !important;
            margin: auto !important;
        }
        """
    ) as interface:
        # Título y descripción
        gr.Markdown("# 🌐 Orquestador con Servidor MCP HTTP (Remoto)")
        gr.Markdown(f"""
        **Ejemplo de Punto 2 (Remoto)**: Orquestador local, herramientas en servidor MCP HTTP
        
        **Arquitectura:**
        - 🧠 Orquestador: Cliente local (decide qué herramienta usar)
        - 🔧 Herramientas: Servidor MCP remoto vía HTTP (ejecuta las funciones)
        - 🔌 Comunicación: SSE (Server-Sent Events) sobre HTTP
        - 📡 Servidor: `{SERVER_URL}`
        
        **Ventajas del servidor HTTP:**
        - ✅ Accesible desde cualquier máquina en la red
        - ✅ Múltiples clientes pueden conectarse simultáneamente
        - ✅ Escalable (puede estar en un servidor dedicado)
        - ✅ Fácil de desplegar en la nube
        
        **Herramientas disponibles:**
        - ➕ Sumar dos números
        - ✖️ Multiplicar dos números  
        - 👤 Obtener información de usuario
        - 🌤️ Consultar clima de una ubicación
        """)
        # Chatbot
        chatbot = gr.Chatbot(
            value=[],
            height=450,
            show_label=False,
            container=True,
            bubble_full_width=False,
            type="tuples",
        )
        # Input
        with gr.Row():
            user_input = gr.Textbox(
                placeholder="Escribe tu mensaje aquí... (ej: ¿Cuánto es 5 + 3?)",
                show_label=False,
                container=False,
                scale=4
            )
            send_btn = gr.Button("Enviar", variant="primary", scale=1)
        # Control
        with gr.Row():
            clear_btn = gr.Button("🗑️ Limpiar Chat", variant="secondary")
        # Ejemplos
        gr.Markdown("### 💡 Prueba estos ejemplos:")
        with gr.Row():
            example_1 = gr.Button("➕ ¿Cuánto es 5 + 3?", size="sm")
            example_2 = gr.Button("✖️ Multiplica 7 por 8", size="sm")
        with gr.Row():
            example_3 = gr.Button("👤 Info del usuario 123", size="sm")
            example_4 = gr.Button("🌤️ Clima en Madrid", size="sm")
        # Handlers
        send_btn.click(
            process_chat,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input]
        )
        user_input.submit(
            process_chat,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input]
        )
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, user_input]
        )
        example_1.click(lambda: "¿Cuánto es 5 + 3?", outputs=user_input)
        example_2.click(lambda: "Multiplica 7 por 8", outputs=user_input)
        example_3.click(lambda: "Dame información del usuario 123", outputs=user_input)
        example_4.click(lambda: "¿Qué clima hace en Madrid?", outputs=user_input)
    return interface

if __name__ == "__main__":
    main = create_gradio_interface()
    main.launch(server_name="0.0.0.0", server_port=7863, share=False, debug=False, show_error=True, inbrowser=False)

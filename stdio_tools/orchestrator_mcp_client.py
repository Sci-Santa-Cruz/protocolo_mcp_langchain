#!/usr/bin/env python3
"""
Interfaz Gradio para Orquestador con Cliente MCP
Punto 2: UI para orquestador en cliente, herramientas en servidor MCP
"""

import asyncio
import gradio as gr
from typing import List, Tuple
import os
from dotenv import load_dotenv

# Cargar variables
load_dotenv()

# Modo diagnóstico: si MCP_DUMMY=1, no llama MCP y responde de inmediato
MCP_DUMMY = os.getenv("MCP_DUMMY") == "1"

# NO importar MCPOrchestrator hasta que se necesite
_orchestrator = None

def get_orchestrator():
    """Lazy loading del orquestador"""
    global _orchestrator
    if _orchestrator is None:
        # Import solo cuando se necesita
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from orchestrators import MCPOrchestrator
        
        # Crear con ruta absoluta
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "tools_server.py")
        _orchestrator = MCPOrchestrator(server_path=server_path)
    return _orchestrator

# ===============================================
# FUNCIONES PARA GRADIO
# ===============================================
async def process_chat_async(message: str, history: List[List[str]]) -> Tuple[List[List[str]], str]:
    """Procesa un mensaje de forma asíncrona con logs y timeout para evitar spinner infinito."""
    if not message.strip():
        return history, ""
    
    try:
        # Log: inicio
        print(f"[process_chat_async] Recibido mensaje: {message}")

        # Modo diagnóstico: evita MCP totalmente
        if MCP_DUMMY:
            response = f"[DUMMY] Echo: {message}"
        else:
            orchestrator = get_orchestrator()

            # Timeout duro para evitar espera infinita
            response = await asyncio.wait_for(
                orchestrator.process_message(message),
                timeout=25
            )

        # Log: éxito
        print("[process_chat_async] Respuesta lista")

        history.append([message, response])
        return history, ""
    except asyncio.TimeoutError:
        error_msg = "❌ Timeout: el servidor no respondió a tiempo. Intenta de nuevo."
        print("[process_chat_async] Timeout esperando respuesta")
        history.append([message, error_msg])
        return history, ""
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(f"[process_chat_async] Error: {e}")
        history.append([message, error_msg])
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
        title="🔧 Orquestador con Servidor MCP",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1000px !important;
            margin: auto !important;
        }
        """
    ) as interface:
        
        gr.Markdown("# 🔧 Orquestador con Servidor MCP")
        gr.Markdown("""
        **Ejemplo de Punto 2**: Orquestador local, herramientas en servidor MCP
        
        **Arquitectura:**
        - 🧠 Orquestador: Cliente (decide qué herramienta usar)
        - 🔧 Herramientas: Servidor MCP (ejecuta las funciones)
        - 🔌 Comunicación: stdio (subproceso)
        
        **Herramientas disponibles:**
        - ➕ Sumar dos números
        - ✖️ Multiplicar dos números  
        - 👤 Obtener información de usuario
        - 🌤️ Consultar clima de una ubicación
        """)
        
        chatbot = gr.Chatbot(
            value=[],
            height=450,
            show_label=False,
            container=True,
            bubble_full_width=False,
            type="messages",
        )
        
        with gr.Row():
            user_input = gr.Textbox(
                placeholder="Escribe tu mensaje aquí... (ej: ¿Cuánto es 5 + 3?)",
                show_label=False,
                container=False,
                scale=4
            )
            send_btn = gr.Button("Enviar", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ Limpiar Chat", variant="secondary")
        
        gr.Markdown("### 💡 Prueba estos ejemplos:")
        with gr.Row():
            example_1 = gr.Button("➕ ¿Cuánto es 5 + 3?", size="sm")
            example_2 = gr.Button("✖️ Multiplica 7 por 8", size="sm")
        with gr.Row():
            example_3 = gr.Button("👤 Info del usuario 123", size="sm")
            example_4 = gr.Button("🌤️ Clima en Madrid", size="sm")
        
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

# ===============================================
# FUNCIÓN PRINCIPAL
# ===============================================
def main():
    """Función principal para ejecutar el chatbot"""
    print("🚀 Iniciando Orquestador con Cliente MCP + Gradio...")
    print("📡 Conectando con servidor MCP (tools_server.py)...")
    print("\n💡 Ejemplos de mensajes:")
    print("   - '¿Cuánto es 5 + 3?'")
    print("   - 'Multiplica 7 por 8'")
    print("   - 'Dame información del usuario 123'")
    print("   - '¿Qué clima hace en Madrid?'")
    
    interface = create_gradio_interface()
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        debug=False,
        show_error=True,
        inbrowser=False,
    )

if __name__ == "__main__":
    main()

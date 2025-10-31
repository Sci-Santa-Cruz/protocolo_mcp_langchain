#!/usr/bin/env python3
"""
Interfaz Gradio para Cliente Simple
Punto 3: UI para cliente simple que solo envía/recibe mensajes del servidor con orquestador
"""

import asyncio
import gradio as gr
from typing import List, Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orchestrators import SimpleMCPClient

# ===============================================
# INSTANCIA GLOBAL DEL CLIENTE
# ===============================================
client = SimpleMCPClient()

# ===============================================
# FUNCIONES PARA GRADIO
# ===============================================
async def process_chat_async(message: str, history: List[List[str]]) -> Tuple[List[List[str]], str]:
    """Procesa un mensaje de forma asíncrona"""
    if not message.strip():
        return history, ""
    
    try:
        # Enviar mensaje al servidor MCP
        response = await client.send_message(message)
        
        # Actualizar historial
        history.append([message, response])
        
        return history, ""
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
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
        title="🌐 Cliente Simple - Servidor con Orquestador",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1000px !important;
            margin: auto !important;
        }
        """
    ) as interface:
        
        # Título y descripción
        gr.Markdown("# 🌐 Cliente Simple - Servidor con Orquestador")
        gr.Markdown("""
        **Ejemplo de Punto 3**: Todo en el servidor MCP
        
        **Arquitectura:**
        - 🌐 Cliente: Solo envía mensajes y recibe respuestas
        - 🧠 Servidor MCP: Tiene el orquestador completo y todas las herramientas
        - 🔌 Comunicación: stdio (subproceso)
        
        **Ventajas:**
        - ✅ Cliente muy simple y ligero
        - ✅ Toda la lógica centralizada en el servidor
        - ✅ Fácil de escalar y mantener
        
        **Herramientas disponibles en el servidor:**
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
        )
        
        # Input del usuario
        with gr.Row():
            user_input = gr.Textbox(
                placeholder="Escribe tu mensaje aquí... (ej: ¿Cuánto es 5 + 3?)",
                show_label=False,
                container=False,
                scale=4
            )
            send_btn = gr.Button("Enviar", variant="primary", scale=1)
        
        # Botones de control
        with gr.Row():
            clear_btn = gr.Button("🗑️ Limpiar Chat", variant="secondary")
        
        # Mensajes de ejemplo
        gr.Markdown("### 💡 Prueba estos ejemplos:")
        with gr.Row():
            example_1 = gr.Button("➕ ¿Cuánto es 5 + 3?", size="sm")
            example_2 = gr.Button("✖️ Multiplica 7 por 8", size="sm")
        with gr.Row():
            example_3 = gr.Button("👤 Info del usuario 123", size="sm")
            example_4 = gr.Button("🌤️ Clima en Madrid", size="sm")
        
        # Event handlers
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
        
        # Ejemplos
        example_1.click(lambda: "¿Cuánto es 5 + 3?", outputs=user_input)
        example_2.click(lambda: "Multiplica 7 por 8", outputs=user_input)
        example_3.click(lambda: "Dame información del usuario 123", outputs=user_input)
        example_4.click(lambda: "¿Qué clima hace en Madrid?", outputs=user_input)
        
        # Mensaje de bienvenida
        interface.load(
            lambda: [[None, "¡Hola! Soy un cliente simple conectado a un servidor MCP con orquestador completo. Toda la lógica está en el servidor. ¿En qué puedo ayudarte?"]],
            outputs=chatbot
        )
    
    return interface

# ===============================================
# FUNCIÓN PRINCIPAL
# ===============================================
def main():
    """Función principal para ejecutar el chatbot"""
    print("🚀 Iniciando Cliente Simple con Gradio...")
    print("📡 Conectando con servidor MCP con orquestador (orchestrator_server.py)...")
    print("\n💡 Ejemplos de mensajes:")
    print("   - '¿Cuánto es 5 + 3?'")
    print("   - 'Multiplica 7 por 8'")
    print("   - 'Dame información del usuario 123'")
    print("   - '¿Qué clima hace en Madrid?'")
    
    interface = create_gradio_interface()
    
    # Configuración del servidor
    interface.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        debug=True,
        show_error=True,
        inbrowser=True,
    )

if __name__ == "__main__":
    main()


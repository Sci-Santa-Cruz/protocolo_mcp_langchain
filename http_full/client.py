#!/usr/bin/env python3
"""
Interfaz Gradio para Cliente HTTP Full
Punto Full HTTP: UI para cliente que envía/recibe al orquestador HTTP completo
"""
import asyncio
import gradio as gr
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Tuple
from dotenv import load_dotenv
from ..orchestrators import SimpleMCPClientHTTP

# Cargar .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Cliente HTTP
client = SimpleMCPClientHTTP(server_url=os.getenv('SERVER_URL', 'http://localhost:8001/sse'))

async def process_chat_async(message: str, history: List[Tuple[str,str]]) -> Tuple[List[Tuple[str,str]], str]:
    if not message.strip(): return history, ""
    try:
        response = await client.send_message(message)
        history.append((message, response))
        return history, ""
    except Exception as e:
        msg = f"❌ Error: {e}"
        history.append((message, msg))
        return history, ""

def process_chat(message, history):
    return asyncio.run(process_chat_async(message, history))

def clear_chat(): return [], ""

# Interfaz Gradio
def create_interface():
    with gr.Blocks(title="Cliente HTTP Full MCP") as iface:
        gr.Markdown("# Cliente HTTP Full MCP")
        chatbot = gr.Chatbot(type="tuples")
        inp = gr.Textbox(placeholder="Mensaje...")
        btn = gr.Button("Enviar")
        btn.click(process_chat, [inp, chatbot], [chatbot, inp])
        gr.Button("🗑️ Limpiar").click(clear_chat, None, [chatbot, inp])
    return iface

if __name__ == "__main__":
    create_interface().launch(server_name="0.0.0.0", server_port=7862, debug=False, inbrowser=False)

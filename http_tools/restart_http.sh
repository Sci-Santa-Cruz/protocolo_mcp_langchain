#!/usr/bin/env bash
set -e

# Directorio del stack HTTP-MCP
dir="/home/mar_anta_ruz/kiwi_gpt_service/mcp_examples/http_tools"
cd "$dir"

echo "1. Deteniendo servicios..."
docker compose down

echo "2. Reconstruyendo e iniciando servicios en modo detach..."
docker compose up --build -d

echo "3. Verificando estado de los servicios..."
docker compose ps

echo "\n✅ Stack HTTP-MCP levantado."
echo "   - Servidor TCP SSe en http://localhost:8000/sse"
echo "   - GUI Gradio en http://localhost:7863"

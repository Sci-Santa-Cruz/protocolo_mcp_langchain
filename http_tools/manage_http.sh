#!/usr/bin/env bash
set -e

# Ir al directorio del stack HTTP-MCP
cd "$(dirname "$0")"

echo "1) Deteniendo servicios..."
docker compose down

echo "2) Reconstruyendo e iniciando en background..."
docker compose up --build -d

echo "3) Estado de servicios:"
docker compose ps

echo "\n✅ Stack HTTP-MCP activo"
echo "   - API SSE en http://localhost:8000/sse"
echo "   - GUI en http://localhost:7863"

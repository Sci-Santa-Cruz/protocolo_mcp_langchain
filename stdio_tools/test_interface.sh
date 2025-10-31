#!/bin/bash

echo "=== PRUEBA AUTOMATIZADA DE LA INTERFAZ ==="
echo ""

# Matar procesos previos
pkill -9 -f orchestrator_mcp_client.py 2>/dev/null
sleep 1

# Ejecutar en background
echo "1. Iniciando servidor..."
cd /home/mar_anta_ruz/kiwi_gpt_service/mcp_examples/stdio_tools
python orchestrator_mcp_client.py > /tmp/gradio_output.log 2>&1 &
PID=$!
echo "   PID: $PID"

# Esperar a que inicie
echo "2. Esperando 8 segundos para que inicie..."
sleep 8

# Verificar que el proceso existe
if ps -p $PID > /dev/null; then
    echo "   ✅ Proceso corriendo"
else
    echo "   ❌ Proceso murió"
    cat /tmp/gradio_output.log
    exit 1
fi

# Verificar puerto
echo "3. Verificando puerto 7861..."
if ss -tuln | grep -q 7861; then
    echo "   ✅ Puerto 7861 activo"
else
    echo "   ❌ Puerto no está en escucha"
    cat /tmp/gradio_output.log
    kill $PID
    exit 1
fi

# Probar HTTP
echo "4. Probando HTTP GET /..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:7861)
echo "   Código HTTP: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Servidor responde correctamente"
else
    echo "   ❌ Servidor no responde con 200"
    cat /tmp/gradio_output.log
    kill $PID
    exit 1
fi

# Probar si carga el HTML
echo "5. Verificando contenido HTML..."
if curl -s http://localhost:7861 | grep -q "gradio_config"; then
    echo "   ✅ HTML con configuración de Gradio detectado"
else
    echo "   ❌ HTML no contiene configuración de Gradio"
    kill $PID
    exit 1
fi

echo ""
echo "=== ✅ TODAS LAS PRUEBAS PASARON ==="
echo ""
echo "Servidor corriendo en: http://localhost:7861"
echo "PID: $PID"
echo "Logs en: /tmp/gradio_output.log"
echo ""
echo "Para detener: kill $PID"
echo "Para ver logs: tail -f /tmp/gradio_output.log"



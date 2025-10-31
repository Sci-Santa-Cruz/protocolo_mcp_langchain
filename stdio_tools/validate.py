#!/usr/bin/env python3
import subprocess
import time
import sys
import requests

print("=== VALIDACIÓN AUTOMATIZADA ===\n")

# 1. Matar procesos previos
print("1. Matando procesos previos...")
subprocess.run(["pkill", "-9", "-f", "orchestrator_mcp_client.py"], 
               stderr=subprocess.DEVNULL)
time.sleep(2)

# 2. Iniciar servidor
print("2. Iniciando servidor...")
proc = subprocess.Popen(
    ["python", "orchestrator_mcp_client.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd="/home/mar_anta_ruz/kiwi_gpt_service/mcp_examples/stdio_tools"
)
print(f"   PID: {proc.pid}")
time.sleep(8)

# 3. Verificar que está corriendo
print("3. Verificando proceso...")
if proc.poll() is None:
    print("   ✅ Proceso corriendo")
else:
    print("   ❌ Proceso murió")
    stdout, stderr = proc.communicate()
    print("STDOUT:", stdout.decode())
    print("STDERR:", stderr.decode())
    sys.exit(1)

# 4. Verificar puerto
print("4. Verificando puerto 7861...")
result = subprocess.run(["ss", "-tuln"], capture_output=True, text=True)
if "7861" in result.stdout:
    print("   ✅ Puerto activo")
else:
    print("   ❌ Puerto no activo")
    proc.kill()
    sys.exit(1)

# 5. Probar HTTP
print("5. Probando HTTP...")
try:
    response = requests.get("http://localhost:7861", timeout=5)
    print(f"   Código: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Servidor responde")
    else:
        print(f"   ❌ Código incorrecto")
        proc.kill()
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    proc.kill()
    sys.exit(1)

# 6. Verificar contenido
print("6. Verificando contenido HTML...")
if "gradio_config" in response.text:
    print("   ✅ HTML válido de Gradio")
else:
    print("   ❌ HTML inválido")
    proc.kill()
    sys.exit(1)

print("\n=== ✅ TODAS LAS PRUEBAS PASARON ===")
print(f"\n🌐 Servidor funcionando: http://localhost:7861")
print(f"🔧 PID: {proc.pid}")
print(f"\n⏸️  Para detener: kill {proc.pid}")
print("\nEl servidor seguirá corriendo...")



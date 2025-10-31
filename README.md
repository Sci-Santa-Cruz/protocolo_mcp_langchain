# Ejemplos MCP - Model Context Protocol

Ejemplos de implementación de MCP con LangChain para Kiwi GPT.

## 📋 Prerequisitos

```bash
# Instalar dependencias
pip install langchain-mcp-adapters
pip install gradio langchain langchain-openai langchain-core mcp python-dotenv

# Configurar API Key de OpenAI
export OPENAI_API_KEY="tu-api-key-aqui"
# O crear archivo .env en la raíz del proyecto
```

## 🗂️ Estructura

```
mcp_examples/
├── orchestrators.py        # Código común: clases, herramientas, schemas
├── README.md
├── local/                  # Punto 1: Todo local (sin MCP)
│   └── orchestrator_local_gradio.py
├── stdio_tools/            # Punto 2: Herramientas en servidor MCP (stdio)
│   ├── tools_server.py
│   └── orchestrator_mcp_client.py
├── http_tools/             # Punto 2: Herramientas en servidor MCP (HTTP)
│   ├── tools_server_http.py
│   └── orchestrator_mcp_client_http.py
└── stdio_full/             # Punto 3: Todo en servidor MCP (stdio)
    ├── orchestrator_server.py
    └── simple_client.py
```

## 🚀 Cómo ejecutar

### 1. Local (todo en un proceso, sin MCP)
```bash
cd /home/mar_anta_ruz/kiwi_gpt_service/mcp_examples/local
python orchestrator_local_gradio.py
```
- **URL:** http://localhost:7860
- **Descripción:** Orquestador y herramientas en el mismo proceso
- **Sin MCP:** Usa LangChain directamente

### 2. Herramientas en servidor MCP local (stdio)
```bash
cd /home/mar_anta_ruz/kiwi_gpt_service/mcp_examples/stdio_tools
python orchestrator_mcp_client.py
```
- **URL:** http://localhost:7861
- **Descripción:** Orquestador en cliente, herramientas en servidor MCP
- **Comunicación:** stdio (subproceso automático)
- **El servidor tools_server.py se lanza automáticamente**

### 3. Herramientas en servidor MCP HTTP (remoto)
```bash
cd /home/mar_anta_ruz/kiwi_gpt_service/mcp_examples/http_tools

# Terminal 1 - Servidor MCP HTTP
python tools_server_http.py
# Escucha en http://0.0.0.0:8000/sse

# Terminal 2 - Cliente con Gradio (en otra terminal)
python orchestrator_mcp_client_http.py
# Interfaz en http://localhost:7863
```
- **URL Cliente:** http://localhost:7863
- **URL Servidor:** http://localhost:8000/sse
- **Descripción:** Servidor MCP accesible por HTTP (puede estar en otra máquina)
- **Ventajas:** Múltiples clientes, servidor remoto, escalable

### 4. Todo en servidor MCP (stdio)
```bash
cd /home/mar_anta_ruz/kiwi_gpt_service/mcp_examples/stdio_full
python simple_client.py
```
- **URL:** http://localhost:7862
- **Descripción:** Cliente simple, todo el orquestador en servidor MCP
- **Comunicación:** stdio (subproceso automático)
- **El servidor orchestrator_server.py se lanza automáticamente**

## Qué hace cada uno

| Ejemplo | Orquestador | Herramientas | Comunicación | Puerto |
|---------|-------------|--------------|--------------|--------|
| local | Local | Local | N/A | 7860 |
| stdio_tools | Cliente | Servidor local | stdio | 7861 |
| http_tools | Cliente | Servidor HTTP | HTTP/SSE | 7863 |
| stdio_full | Servidor | Servidor | stdio | 7862 |

## 📝 Archivo común: `orchestrators.py`

Contiene código compartido:
- **Descripciones de herramientas:** JSON con metadata
- **Schemas Pydantic:** Validación de argumentos
- **Herramientas:** `sumar`, `multiplicar`, `getUserInfo`, `getWeather`
- **Clases:**
  - `LocalOrchestrator` - Para `local/` (sin MCP)
  - `MCPOrchestrator` - Para `stdio_tools/` (cliente MCP stdio)
  - `MCPOrchestratorHTTP` - Para `http_tools/` (cliente MCP HTTP)
  - `SimpleMCPClient` - Para `stdio_full/` (cliente simple)

> ⚠️ **Nota:** `stdio_tools/orchestrator_mcp_client.py` tiene su propia clase `MCPOrchestratorStdio` para evitar problemas de rutas.

## 🔧 Herramientas disponibles

Todas las implementaciones exponen las mismas herramientas:

| Herramienta | Descripción | Ejemplo |
|-------------|-------------|---------|
| `sumar` | Suma dos números | "¿Cuánto es 5 + 3?" |
| `multiplicar` | Multiplica dos números | "Multiplica 7 por 8" |
| `getUserInfo` | Info de usuario por ID | "Dame info del usuario 123" |
| `getWeather` | Clima de una ubicación | "¿Qué clima hace en Madrid?" |

## 🐛 Troubleshooting

### Error: "Connection errored out"
- **Causa:** El servidor MCP no se puede iniciar o no responde
- **Solución:** Verifica que `tools_server.py` o `orchestrator_server.py` existen en el directorio correcto

### Error: "ModuleNotFoundError: No module named 'langchain_mcp_adapters'"
```bash
pip install langchain-mcp-adapters
```

### La interfaz no carga
- Verifica que el puerto no esté ocupado:
  ```bash
  ss -tuln | grep PUERTO  # donde PUERTO es 7860, 7861, 7862, o 7863
  ```
- Intenta cambiar el puerto en el código

### El servidor HTTP no conecta
- Asegúrate de ejecutar primero `tools_server_http.py` antes del cliente
- Verifica que el puerto 8000 esté libre
- Verifica la URL en el cliente: `http://localhost:8000/sse`

## 📚 Más información

- [MCP Documentation](https://modelcontextprotocol.io/)
- [LangChain MCP Adapters](https://python.langchain.com/docs/integrations/tools/mcp/)
- [FastMCP](https://github.com/jlowin/fastmcp)

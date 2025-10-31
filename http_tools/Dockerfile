FROM python:3.13-slim
WORKDIR /app
# Copiar todo el código al contenedor
COPY . /app
# Instalar dependencias de servidor y cliente
RUN pip install --no-cache-dir \
    mcp uvicorn python-dotenv \
    gradio langchain langchain-openai langchain-mcp-adapters
# Mostrar logs inmediatamente
ENV PYTHONUNBUFFERED=1

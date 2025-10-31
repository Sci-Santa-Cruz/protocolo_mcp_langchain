FROM python:3.13-slim
WORKDIR /app
# Copy entire repo for HTTP full example
COPY ../.. /app
# Install dependencies at build-time
RUN pip install --no-cache-dir \
    mcp uvicorn python-dotenv \
    gradio langchain langchain-openai langchain-mcp-adapters
ENV PYTHONUNBUFFERED=1

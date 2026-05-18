FROM python:3.12-slim

# Install Node.js 20 and system deps
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    "ibm-watsonx-orchestrate==2.9.0" \
    "fastapi==0.115.0" \
    "uvicorn==0.32.0" \
    "sse-starlette==2.1.3" \
    "httpx==0.27.0" \
    "requests==2.32.3" \
    "pydantic==2.8.0" \
    "pyyaml==6.0.1" \
    "python-dotenv==1.0.0" \
    "openai" \
    "groq"

# Install frontend dependencies
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci

# Copy all source code
COPY backend/ ./backend/
COPY api/ ./api/
COPY frontend/ ./frontend/

# Build Next.js — BACKEND_URL is used server-side by next.config.mjs rewrites
ENV BACKEND_URL=http://localhost:8000
RUN cd frontend && npm run build

# Create writable dirs needed at runtime
RUN mkdir -p backend/generated_agents bob_sessions && \
    chmod -R 777 backend/generated_agents bob_sessions

COPY hf_start.sh /app/start.sh
RUN chmod +x /app/start.sh

# HF Spaces requires port 7860
EXPOSE 7860

CMD ["/app/start.sh"]

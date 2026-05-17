# AgentForge API Documentation

## Overview

The AgentForge API is a FastAPI-based backend that orchestrates the complete agent generation and deployment pipeline. It connects Bob Runner (AI generation) with the ADK Deployment module to provide a seamless REST API for creating watsonx Orchestrate agents.

## Base URL

```
http://localhost:8000
```

## Architecture

```
Frontend (Next.js)
    ↓ HTTP POST
FastAPI Backend
    ↓
Bob Runner → ADK Deployment
    ↓
watsonx Orchestrate
```

## Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "AgentForge API",
  "version": "1.0.0"
}
```

---

### Generate Agent

**POST** `/api/generate-agent`

Generate and deploy an agent from a natural language prompt.

**Request Body:**
```json
{
  "prompt": "Create an agent that fetches top 5 Hacker News stories"
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Agent generation started",
  "stream_url": "/api/stream/550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes:**
- `200 OK`: Task created successfully
- `422 Unprocessable Entity`: Invalid request body

---

### Get Task Status

**GET** `/api/status/{task_id}`

Get the current status of a generation/deployment task.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "stage": "deploying",
  "progress": 60,
  "message": "Deploying agent 'hn_agent' to watsonx Orchestrate...",
  "agent_name": "hn_agent",
  "chat_url": null,
  "errors": [],
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:45.000Z"
}
```

**Status Values:**
- `pending`: Task created, waiting to start
- `running`: Task is executing
- `completed`: Task finished successfully
- `failed`: Task failed with errors

**Stage Values:**
- `initializing`: Task setup
- `generating`: Bob Shell generating agent
- `validating`: Validating generated artifacts
- `deploying`: Deploying to watsonx Orchestrate
- `deployed`: Successfully deployed
- `generation_failed`: Bob generation failed
- `deployment_failed`: Deployment failed
- `error`: Unexpected error

**Status Codes:**
- `200 OK`: Task found
- `404 Not Found`: Task ID doesn't exist

---

### Stream Progress (SSE)

**GET** `/api/stream/{task_id}`

Server-Sent Events stream for real-time progress updates.

**Response Format:**
```
data: {"status":"running","stage":"generating","progress":10,"message":"Calling Bob Shell...","agent_name":null,"chat_url":null,"errors":[]}

data: {"status":"running","stage":"validating","progress":40,"message":"Validating artifacts...","agent_name":"hn_agent","chat_url":null,"errors":[]}

data: {"status":"running","stage":"deploying","progress":60,"message":"Deploying agent...","agent_name":"hn_agent","chat_url":null,"errors":[]}

data: {"status":"completed","stage":"deployed","progress":100,"message":"Agent deployed!","agent_name":"hn_agent","chat_url":"https://orchestrate.ibm.com/agents/hn_agent","errors":[]}
```

**Headers:**
- `Content-Type: text/event-stream`
- `Cache-Control: no-cache`
- `Connection: keep-alive`

**Status Codes:**
- `200 OK`: Stream started
- `404 Not Found`: Task ID doesn't exist

---

### List Tasks

**GET** `/api/tasks`

List all tasks (for debugging/admin).

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "stage": "deployed",
      "progress": 100,
      "agent_name": "hn_agent",
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ]
}
```

---

### Delete Task

**DELETE** `/api/tasks/{task_id}`

Delete a task (cleanup).

**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Task deleted
- `404 Not Found`: Task ID doesn't exist

---

## Usage Examples

### Python

```python
import requests
import json

# 1. Generate agent
response = requests.post(
    "http://localhost:8000/api/generate-agent",
    json={"prompt": "Create an agent that fetches weather"}
)
result = response.json()
task_id = result["task_id"]

# 2. Poll for status
import time
while True:
    response = requests.get(f"http://localhost:8000/api/status/{task_id}")
    status = response.json()
    
    print(f"[{status['progress']}%] {status['message']}")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(2)

# 3. Get final result
if status['status'] == 'completed':
    print(f"Agent deployed: {status['chat_url']}")
else:
    print(f"Failed: {status['errors']}")
```

### JavaScript (Fetch API)

```javascript
// 1. Generate agent
const response = await fetch('http://localhost:8000/api/generate-agent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'Create an agent that fetches weather'
  })
});

const { task_id, stream_url } = await response.json();

// 2. Stream progress (SSE)
const eventSource = new EventSource(`http://localhost:8000${stream_url}`);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`[${data.progress}%] ${data.message}`);
  
  if (data.status === 'completed') {
    console.log(`Agent deployed: ${data.chat_url}`);
    eventSource.close();
  } else if (data.status === 'failed') {
    console.error(`Failed: ${data.errors}`);
    eventSource.close();
  }
};
```

### cURL

```bash
# 1. Generate agent
curl -X POST http://localhost:8000/api/generate-agent \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Create an agent that fetches weather"}'

# Response: {"task_id":"...","status":"pending",...}

# 2. Get status
curl http://localhost:8000/api/status/TASK_ID

# 3. Stream progress (SSE)
curl -N http://localhost:8000/api/stream/TASK_ID
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message"
}
```

### Common Errors

**422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**404 Not Found**
```json
{
  "detail": "Task not found"
}
```

---

## Task Lifecycle

```
1. POST /api/generate-agent
   ↓
2. Task created (status: pending)
   ↓
3. Background task starts
   ↓
4. Stage: generating (progress: 10-40%)
   - Bob Shell generates agent YAML + tools
   ↓
5. Stage: validating (progress: 40-60%)
   - Validate ADK schema
   ↓
6. Stage: deploying (progress: 60-100%)
   - Import tools to Orchestrate
   - Import agent to Orchestrate
   ↓
7. Status: completed or failed
   - If completed: chat_url available
   - If failed: errors array populated
```

---

## Rate Limiting

Currently no rate limiting is implemented. In production, consider:
- Rate limiting per IP
- Task queue with max concurrent tasks
- Timeout for long-running tasks

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (Next.js dev)
- `http://localhost:3001`
- `https://agentforge.vercel.app` (production)

To add more origins, update `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend.com"],
    ...
)
```

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Test endpoints directly
- See request/response schemas
- View example payloads

---

## Deployment

### Development

```bash
# Start the server
./start_api.sh

# Or manually
conda activate watsonx
cd api
python main.py
```

### Production

```bash
# Using Gunicorn
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# Using Docker
docker build -t agentforge-api .
docker run -p 8000:8000 agentforge-api
```

---

## Monitoring

### Health Check

```bash
# Check if API is running
curl http://localhost:8000/health
```

### Logs

The API logs to stdout. In production, configure proper logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Security Considerations

1. **Authentication**: Add API key or JWT authentication
2. **Rate Limiting**: Prevent abuse
3. **Input Validation**: Already handled by Pydantic
4. **CORS**: Restrict to known origins
5. **HTTPS**: Use in production
6. **Secrets**: Store credentials in environment variables

---

## Troubleshooting

### API won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Check Conda environment
conda activate watsonx
python -c "import fastapi; print(fastapi.__version__)"
```

### Tasks stuck in "running"

- Check backend logs for errors
- Verify Orchestrate CLI is accessible
- Check Conda environment is active

### SSE stream not working

- Ensure client supports Server-Sent Events
- Check CORS configuration
- Verify task_id is valid

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [DEPLOYMENT_SETUP.md](DEPLOYMENT_SETUP.md) - Deployment guide
- [README.md](README.md) - Project overview
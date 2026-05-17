"""
API Routes for AgentForge

Endpoints:
- POST /api/generate-agent: Generate and deploy an agent
- GET /api/status/{task_id}: Get generation/deployment status
- GET /api/stream/{task_id}: Server-Sent Events stream for progress
"""

import sys
import asyncio
import uuid
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Use groq_runner (recommended - simple, fast, no IBM provisioning needed)
# Alternative: watsonx_runner (requires IBM Cloud project provisioning)
from groq_runner import generate_agent
from deploy_agent import deploy_agent
from models import AgentGenerationResult, DeploymentResult

router = APIRouter()

# In-memory task storage (in production, use Redis or database)
tasks: Dict[str, dict] = {}


class GenerateAgentRequest(BaseModel):
    """Request model for agent generation."""
    prompt: str = Field(
        ...,
        description="Natural language description of the agent to create",
        min_length=10,
        max_length=1000,
        examples=["Create an agent that fetches top 5 Hacker News stories"]
    )


class GenerateAgentResponse(BaseModel):
    """Response model for agent generation."""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Initial status")
    message: str = Field(..., description="Status message")
    stream_url: str = Field(..., description="URL for progress streaming")


class TaskStatus(BaseModel):
    """Task status model."""
    task_id: str
    status: str
    stage: str
    progress: int
    message: str
    agent_name: Optional[str] = None
    chat_url: Optional[str] = None
    errors: list[str] = []
    created_at: str
    updated_at: str


def create_task(prompt: str) -> str:
    """Create a new task and return its ID."""
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "prompt": prompt,
        "status": "pending",
        "stage": "initializing",
        "progress": 0,
        "message": "Task created, waiting to start...",
        "agent_name": None,
        "chat_url": None,
        "errors": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "generation_result": None,
        "deployment_result": None
    }
    return task_id


def update_task(task_id: str, **kwargs):
    """Update task status."""
    if task_id in tasks:
        tasks[task_id].update(kwargs)
        tasks[task_id]["updated_at"] = datetime.utcnow().isoformat()


async def generate_and_deploy_agent(task_id: str, prompt: str):
    """
    Background task that generates and deploys an agent.
    
    Updates task status at each stage for SSE streaming.
    """
    try:
        # Stage 1: Bob Generation
        update_task(
            task_id,
            status="running",
            stage="generating",
            progress=10,
            message="Calling Bob Shell to generate agent..."
        )
        
        # Call Bob Runner
        generation_result = generate_agent(prompt, max_retries=2)
        
        # Store generation result
        update_task(task_id, generation_result=generation_result)
        
        # Check if generation succeeded
        if generation_result.status != "ok":
            update_task(
                task_id,
                status="failed",
                stage="generation_failed",
                progress=100,
                message="Agent generation failed",
                errors=generation_result.errors
            )
            return
        
        # Stage 2: Validation
        update_task(
            task_id,
            status="running",
            stage="validating",
            progress=40,
            message="Validating generated artifacts..."
        )
        
        # Extract agent name
        import yaml
        try:
            agent_data = yaml.safe_load(generation_result.agent_yaml)
            agent_name = agent_data.get('name', 'unknown_agent')
        except:
            agent_name = 'unknown_agent'
        
        update_task(task_id, agent_name=agent_name)
        
        # Stage 3: Deployment
        update_task(
            task_id,
            status="running",
            stage="deploying",
            progress=60,
            message=f"Deploying agent '{agent_name}' to watsonx Orchestrate..."
        )
        
        # Call Deployment Pipeline
        deployment_result = deploy_agent(generation_result)
        
        # Store deployment result
        update_task(task_id, deployment_result=deployment_result)
        
        # Check if deployment succeeded
        if deployment_result.status != "deployed":
            update_task(
                task_id,
                status="failed",
                stage="deployment_failed",
                progress=100,
                message="Agent deployment failed",
                errors=deployment_result.errors
            )
            return
        
        # Stage 4: Success
        update_task(
            task_id,
            status="completed",
            stage="deployed",
            progress=100,
            message=f"Agent '{deployment_result.agent_name}' deployed successfully!",
            agent_name=deployment_result.agent_name,
            chat_url=deployment_result.chat_url
        )
        
    except Exception as e:
        # Handle unexpected errors
        update_task(
            task_id,
            status="failed",
            stage="error",
            progress=100,
            message=f"Unexpected error: {str(e)}",
            errors=[str(e)]
        )


@router.post("/generate-agent", response_model=GenerateAgentResponse)
async def generate_agent_endpoint(
    request: GenerateAgentRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate and deploy an agent from a natural language prompt.
    
    This endpoint:
    1. Creates a task
    2. Starts background generation/deployment
    3. Returns task ID and stream URL
    
    Use the stream URL to get real-time progress updates via SSE.
    """
    # Create task
    task_id = create_task(request.prompt)
    
    # Start background task
    background_tasks.add_task(generate_and_deploy_agent, task_id, request.prompt)
    
    return GenerateAgentResponse(
        task_id=task_id,
        status="pending",
        message="Agent generation started",
        stream_url=f"/api/stream/{task_id}"
    )


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """
    Get the current status of a task.
    
    Returns detailed information about the generation/deployment progress.
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    return TaskStatus(
        task_id=task["task_id"],
        status=task["status"],
        stage=task["stage"],
        progress=task["progress"],
        message=task["message"],
        agent_name=task.get("agent_name"),
        chat_url=task.get("chat_url"),
        errors=task.get("errors", []),
        created_at=task["created_at"],
        updated_at=task["updated_at"]
    )


@router.get("/stream/{task_id}")
async def stream_task_progress(task_id: str):
    """
    Server-Sent Events stream for real-time task progress.
    
    Streams updates as the agent is generated and deployed.
    Frontend can listen to this stream to show live progress.
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    async def event_generator():
        """Generate SSE events for task progress."""
        last_update = None
        
        while True:
            task = tasks.get(task_id)
            if not task:
                break
            
            # Send update if task changed
            current_update = task["updated_at"]
            if current_update != last_update:
                # Format as SSE
                data = {
                    "status": task["status"],
                    "stage": task["stage"],
                    "progress": task["progress"],
                    "message": task["message"],
                    "agent_name": task.get("agent_name"),
                    "chat_url": task.get("chat_url"),
                    "errors": task.get("errors", [])
                }
                
                import json
                yield f"data: {json.dumps(data)}\n\n"
                
                last_update = current_update
            
            # Stop streaming if task is complete or failed
            if task["status"] in ["completed", "failed"]:
                break
            
            # Wait before checking again
            await asyncio.sleep(0.5)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/tasks")
async def list_tasks():
    """
    List all tasks (for debugging/admin).
    
    In production, this should be paginated and filtered.
    """
    return {
        "tasks": [
            {
                "task_id": task["task_id"],
                "status": task["status"],
                "stage": task["stage"],
                "progress": task["progress"],
                "agent_name": task.get("agent_name"),
                "created_at": task["created_at"]
            }
            for task in tasks.values()
        ]
    }


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a task (cleanup).
    
    In production, tasks should be automatically cleaned up after a certain time.
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks[task_id]
    
    return {"message": "Task deleted successfully"}

# Made with Bob

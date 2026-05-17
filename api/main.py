"""
FastAPI Backend for AgentForge (KAN-12)

This is the orchestrator layer that connects:
- Bob Runner (agent generation)
- ADK Deployment (watsonx Orchestrate deployment)
- Frontend (Next.js UI)

It provides REST endpoints and Server-Sent Events for real-time progress updates.
"""

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from routes import router

# Create FastAPI app
app = FastAPI(
    title="AgentForge API",
    description="Backend API for AgentForge - 'Vercel for AI Agents'",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AgentForge API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AgentForge API",
        "description": "Backend for generating and deploying watsonx Orchestrate agents",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

# Made with Bob

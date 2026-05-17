"""
Test script for AgentForge FastAPI backend.

Tests the complete API flow:
1. POST /api/generate-agent
2. GET /api/stream/{task_id} (SSE)
3. GET /api/status/{task_id}
"""

import requests
import json
import time
from sseclient import SSEClient  # pip install sseclient-py

API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint."""
    print("=" * 60)
    print("Testing Health Check")
    print("=" * 60)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_generate_agent():
    """Test the agent generation endpoint."""
    print("=" * 60)
    print("Testing Agent Generation")
    print("=" * 60)
    
    # Send generation request
    payload = {
        "prompt": "Create an agent that fetches the top 5 Hacker News stories"
    }
    
    print(f"Sending request: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{API_BASE_URL}/api/generate-agent", json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    task_id = result["task_id"]
    stream_url = result["stream_url"]
    
    print(f"\nTask ID: {task_id}")
    print(f"Stream URL: {API_BASE_URL}{stream_url}")
    print()
    
    return task_id


def test_stream_progress(task_id: str):
    """Test the SSE stream endpoint."""
    print("=" * 60)
    print("Testing Progress Stream (SSE)")
    print("=" * 60)
    
    stream_url = f"{API_BASE_URL}/api/stream/{task_id}"
    print(f"Connecting to: {stream_url}\n")
    
    try:
        messages = SSEClient(stream_url)
        
        for msg in messages:
            if msg.data:
                data = json.loads(msg.data)
                
                # Display progress
                status = data.get("status")
                stage = data.get("stage")
                progress = data.get("progress")
                message = data.get("message")
                
                print(f"[{progress}%] {stage}: {message}")
                
                # Check if complete
                if status in ["completed", "failed"]:
                    print(f"\nFinal Status: {status}")
                    if data.get("chat_url"):
                        print(f"Chat URL: {data['chat_url']}")
                    if data.get("errors"):
                        print(f"Errors: {data['errors']}")
                    break
    
    except Exception as e:
        print(f"Stream error: {str(e)}")
    
    print()


def test_get_status(task_id: str):
    """Test the status endpoint."""
    print("=" * 60)
    print("Testing Status Endpoint")
    print("=" * 60)
    
    response = requests.get(f"{API_BASE_URL}/api/status/{task_id}")
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    print(f"Status: {json.dumps(result, indent=2)}")
    print()


def test_list_tasks():
    """Test the list tasks endpoint."""
    print("=" * 60)
    print("Testing List Tasks")
    print("=" * 60)
    
    response = requests.get(f"{API_BASE_URL}/api/tasks")
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    print(f"Tasks: {json.dumps(result, indent=2)}")
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AgentForge API Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Health check
    test_health_check()
    
    # Test 2: Generate agent
    task_id = test_generate_agent()
    
    if not task_id:
        print("Failed to create task. Exiting.")
        return
    
    # Test 3: Stream progress (SSE)
    test_stream_progress(task_id)
    
    # Test 4: Get final status
    test_get_status(task_id)
    
    # Test 5: List all tasks
    test_list_tasks()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob

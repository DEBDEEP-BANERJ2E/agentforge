# AgentForge
Type one sentence. Get a deployed watsonx Orchestrate agent in ~90 seconds.

## Setup
pip install ibm-watsonx-orchestrate==2.9.0 httpx==0.27.0 pydantic==2.8.0

## Run
from backend.bob_runner import generate_agent
result = generate_agent("agent that fetches top 5 hacker news stories")
print(result.status, result.agent_yaml)

## Bob Sessions
All Bob task sessions are saved to bob_sessions/ for hackathon submission.

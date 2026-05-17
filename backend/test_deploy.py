"""
End-to-end test for the deployment pipeline.

This test creates mock agent generation results and attempts to deploy them
to watsonx Orchestrate to verify the entire deployment flow works.
"""

from models import AgentGenerationResult, ToolFile, DeploymentResult
from deploy_agent import deploy_agent


def create_mock_agent_result() -> AgentGenerationResult:
    """
    Create a mock AgentGenerationResult for testing.
    
    This simulates what bob_runner.generate_agent() would return.
    """
    # Mock agent YAML
    agent_yaml = """spec_version: v1
kind: native
name: test_weather_agent
description: A test agent that fetches weather information
llm: watsonx/meta-llama/llama-3-2-90b-vision-instruct
style: default
instructions: |
  You are a helpful weather assistant. When users ask about weather,
  use the get_weather tool to fetch current conditions.
tools:
  - get_weather
"""
    
    # Mock tool file
    tool_code = """from ibm_watsonx_orchestrate.agent_builder.tools import tool
import httpx


@tool
async def get_weather(city: str) -> str:
    \"\"\"
    Get current weather for a city.
    
    Args:
        city: Name of the city
        
    Returns:
        Weather description
    \"\"\"
    # Mock implementation - in real scenario would call weather API
    async with httpx.AsyncClient() as client:
        # Simulated API call
        return f"Weather in {city}: Sunny, 72°F"
"""
    
    tool = ToolFile(
        filename="get_weather.py",
        content=tool_code
    )
    
    # Mock requirements.txt
    requirements = """httpx==0.27.0
pydantic==2.8.0
"""
    
    return AgentGenerationResult(
        agent_yaml=agent_yaml,
        tools=[tool],
        requirements_txt=requirements,
        raw_bob_output="[Mock Bob output]",
        bob_session_id="test_session_001",
        status="ok",
        errors=[]
    )


def test_deployment():
    """
    Test the complete deployment pipeline.
    
    Steps:
    1. Create mock agent generation result
    2. Call deploy_agent()
    3. Print results
    4. Verify deployment status
    """
    print("=" * 60)
    print("AgentForge Deployment Test")
    print("=" * 60)
    
    # Step 1: Create mock data
    print("\n[1/3] Creating mock agent generation result...")
    mock_result = create_mock_agent_result()
    print(f"✓ Mock agent: {mock_result.agent_yaml.split('name:')[1].split()[0]}")
    print(f"✓ Tools: {[t.filename for t in mock_result.tools]}")
    
    # Step 2: Deploy
    print("\n[2/3] Deploying to watsonx Orchestrate...")
    print("(This will verify environment, import tools, and import agent)")
    print()
    
    try:
        deployment_result = deploy_agent(mock_result)
    except Exception as e:
        print(f"\n✗ Deployment failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Display results
    print("\n[3/3] Deployment Results")
    print("-" * 60)
    print(f"Status: {deployment_result.status}")
    print(f"Agent Name: {deployment_result.agent_name}")
    print(f"Tools Imported: {deployment_result.tools_imported}")
    print(f"Chat URL: {deployment_result.chat_url}")
    
    if deployment_result.errors:
        print(f"\nErrors ({len(deployment_result.errors)}):")
        for error in deployment_result.errors:
            print(f"  - {error}")
    
    print("\nCLI Output:")
    print("-" * 60)
    print(deployment_result.cli_output)
    print("-" * 60)
    
    # Verify success
    if deployment_result.status == "deployed":
        print("\n✓ DEPLOYMENT SUCCESSFUL!")
        print(f"\nNext steps:")
        print(f"1. Open Orchestrate UI: https://orchestrate.ibm.com")
        print(f"2. Navigate to Agents section")
        print(f"3. Find agent: {deployment_result.agent_name}")
        print(f"4. Test the agent in chat")
    else:
        print(f"\n✗ DEPLOYMENT FAILED: {deployment_result.status}")
        print("\nTroubleshooting:")
        if deployment_result.status == "auth_failed":
            print("  - Run: conda activate watsonx")
            print("  - Run: orchestrate env activate wx0-AWS")
        elif deployment_result.status == "tool_import_failed":
            print("  - Check tool syntax and imports")
            print("  - Verify requirements.txt packages are in allowlist")
        elif deployment_result.status == "agent_import_failed":
            print("  - Check agent YAML schema")
            print("  - Verify all tools were imported successfully")


if __name__ == "__main__":
    test_deployment()

# Made with Bob

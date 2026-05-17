"""
End-to-End Integration Test for AgentForge

This test demonstrates the complete pipeline:
1. User provides a natural language prompt
2. Bob Runner generates agent YAML + tools + requirements
3. Deployment Pipeline deploys to watsonx Orchestrate
4. Returns a live chat URL

This is the CORE DEMO for the hackathon - it shows the entire
"Vercel for AI Agents" concept working end-to-end.
"""

import sys
from pathlib import Path

# Add backend to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from bob_runner import generate_agent
from deploy_agent import deploy_agent
from models import AgentGenerationResult, DeploymentResult


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


def test_end_to_end_pipeline():
    """
    Complete end-to-end test of AgentForge pipeline.
    
    This demonstrates the entire flow from user prompt to deployed agent.
    """
    print_section("🚀 AgentForge End-to-End Integration Test")
    
    # =========================================================================
    # STEP 1: User Input
    # =========================================================================
    print_section("STEP 1: User Input")
    
    user_prompt = "Create an agent that fetches the top 5 Hacker News stories"
    
    print(f"\n📝 User Prompt:")
    print(f"   \"{user_prompt}\"")
    print(f"\n💭 What happens next:")
    print(f"   1. Bob Shell generates agent YAML + Python tools")
    print(f"   2. Output is validated against ADK schema")
    print(f"   3. Agent is deployed to watsonx Orchestrate")
    print(f"   4. Live chat URL is returned")
    
    # =========================================================================
    # STEP 2: Bob Generation
    # =========================================================================
    print_section("STEP 2: Bob Generation (AI Code Generation)")
    
    print("\n🤖 Calling Bob Shell...")
    print("   - Using custom 'Agent Architect' mode")
    print("   - Generating ADK-compatible artifacts")
    print("   - Validating output schema")
    print("   - Retrying on errors (max 2 retries)")
    
    try:
        generation_result = generate_agent(user_prompt, max_retries=2)
    except Exception as e:
        print(f"\n❌ Bob generation failed with exception:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Display generation results
    print_subsection("Generation Results")
    print(f"Status: {generation_result.status}")
    print(f"Session ID: {generation_result.bob_session_id}")
    
    if generation_result.status != "ok":
        print(f"\n❌ Generation failed!")
        print(f"Errors:")
        for error in generation_result.errors:
            print(f"  - {error}")
        print(f"\nRaw Bob Output:")
        print(generation_result.raw_bob_output[:500] + "...")
        return
    
    print(f"\n✅ Generation successful!")
    
    # Display generated artifacts
    print_subsection("Generated Artifacts")
    
    # Parse agent name from YAML
    import yaml
    try:
        agent_data = yaml.safe_load(generation_result.agent_yaml)
        agent_name = agent_data.get('name', 'unknown')
        agent_desc = agent_data.get('description', 'No description')
    except:
        agent_name = 'unknown'
        agent_desc = 'Could not parse'
    
    print(f"\n📄 Agent YAML:")
    print(f"   Name: {agent_name}")
    print(f"   Description: {agent_desc}")
    print(f"   LLM: {agent_data.get('llm', 'unknown')}")
    
    print(f"\n🔧 Tools ({len(generation_result.tools)}):")
    for tool in generation_result.tools:
        print(f"   - {tool.filename}")
        # Show first few lines of tool code
        lines = tool.content.split('\n')[:5]
        for line in lines:
            if line.strip():
                print(f"     {line}")
    
    print(f"\n📦 Requirements:")
    for req in generation_result.requirements_txt.split('\n'):
        if req.strip():
            print(f"   - {req.strip()}")
    
    print(f"\n💾 Session saved to: bob_sessions/{generation_result.bob_session_id}.txt")
    
    # =========================================================================
    # STEP 3: Deployment
    # =========================================================================
    print_section("STEP 3: ADK Deployment (watsonx Orchestrate)")
    
    print("\n🚀 Deploying to watsonx Orchestrate...")
    print("   - Verifying environment (Conda, CLI, auth)")
    print("   - Writing files to generated_agents/")
    print("   - Importing tools via ADK CLI")
    print("   - Importing agent via ADK CLI")
    print("   - Generating chat URL")
    
    try:
        deployment_result = deploy_agent(generation_result)
    except Exception as e:
        print(f"\n❌ Deployment failed with exception:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Display deployment results
    print_subsection("Deployment Results")
    print(f"Status: {deployment_result.status}")
    print(f"Agent Name: {deployment_result.agent_name}")
    
    if deployment_result.status != "deployed":
        print(f"\n❌ Deployment failed!")
        print(f"Errors:")
        for error in deployment_result.errors:
            print(f"  - {error}")
        print(f"\nCLI Output:")
        print(deployment_result.cli_output)
        
        # Provide troubleshooting
        print_subsection("Troubleshooting")
        if deployment_result.status == "auth_failed":
            print("Authentication issue detected:")
            print("  1. Run: conda activate watsonx")
            print("  2. Run: orchestrate env activate wx0-AWS")
            print("  3. Verify: orchestrate agents list")
        elif deployment_result.status == "tool_import_failed":
            print("Tool import issue detected:")
            print("  - Check tool syntax and imports")
            print("  - Verify requirements.txt packages are in allowlist")
            print("  - Review CLI output above for specific errors")
        elif deployment_result.status == "agent_import_failed":
            print("Agent import issue detected:")
            print("  - Check agent YAML schema")
            print("  - Verify all tools were imported successfully")
        
        return
    
    print(f"\n✅ Deployment successful!")
    
    print_subsection("Deployed Agent Details")
    print(f"\n🎯 Agent Name: {deployment_result.agent_name}")
    print(f"🔧 Tools Imported: {', '.join(deployment_result.tools_imported)}")
    print(f"🌐 Chat URL: {deployment_result.chat_url}")
    
    # =========================================================================
    # STEP 4: Success Summary
    # =========================================================================
    print_section("✨ SUCCESS - Agent Deployed!")
    
    print(f"\n🎉 Your agent is now live in watsonx Orchestrate!")
    print(f"\n📍 Agent Details:")
    print(f"   Name: {deployment_result.agent_name}")
    print(f"   Status: Draft (ready for testing)")
    print(f"   Tools: {len(deployment_result.tools_imported)} imported")
    
    print(f"\n🔗 Access Your Agent:")
    print(f"   1. Open: {deployment_result.chat_url}")
    print(f"   2. Or go to: https://orchestrate.ibm.com")
    print(f"   3. Navigate to: Agents → {deployment_result.agent_name}")
    print(f"   4. Click 'Chat' to test the agent")
    
    print(f"\n💬 Try asking:")
    print(f"   \"Show me the top Hacker News stories\"")
    print(f"   \"What are the trending tech articles?\"")
    
    print(f"\n📊 Pipeline Statistics:")
    print(f"   User Prompt → Generated Agent → Deployed")
    print(f"   Total Time: ~90 seconds (typical)")
    print(f"   Bob Session: {generation_result.bob_session_id}")
    print(f"   Files: generated_agents/{deployment_result.agent_name}/")
    
    print_section("🎯 End-to-End Test Complete")
    
    print(f"\nThis demonstrates the core AgentForge value proposition:")
    print(f"  'Type one sentence. Get a deployed agent in ~90 seconds.'")
    print(f"\n✅ All systems operational!")


if __name__ == "__main__":
    test_end_to_end_pipeline()

# Made with Bob

"""
Test script for bob_runner agent generation.
"""

from bob_runner import generate_agent


def main():
    print("Starting agent generation test...")
    print("=" * 80)
    
    # Test prompt
    user_prompt = "agent that converts markdown text to formatted HTML"
    
    print(f"User Prompt: {user_prompt}")
    print("=" * 80)
    print("\nCalling generate_agent()...\n")
    
    # Generate the agent
    result = generate_agent(user_prompt, max_retries=2)
    
    # Print results
    print("=" * 80)
    print(f"Status: {result.status}")
    print("=" * 80)
    
    if result.status == "ok":
        print("\n✅ SUCCESS! Agent generated successfully.\n")
        
        # Print first 200 chars of agent_yaml
        if result.agent_yaml:
            print("Agent YAML (first 200 chars):")
            print("-" * 80)
            print(result.agent_yaml[:200])
            print("...")
            print("-" * 80)
        
        # Print tool filenames
        print(f"\nGenerated Tools ({len(result.tools)}):")
        print("-" * 80)
        for tool in result.tools:
            print(f"  - {tool.filename}")
        print("-" * 80)
        
        # Print requirements info
        if result.requirements_txt:
            req_lines = result.requirements_txt.strip().split('\n')
            print(f"\nRequirements ({len(req_lines)} lines):")
            print("-" * 80)
            print(result.requirements_txt[:200])
            if len(result.requirements_txt) > 200:
                print("...")
            print("-" * 80)
    else:
        print(f"\n❌ FAILED with status: {result.status}\n")
        
        if result.errors:
            print("Errors:")
            print("-" * 80)
            for error in result.errors:
                print(f"  - {error}")
            print("-" * 80)
        
        if result.raw_bob_output:
            print("\nRaw Bob Output (first 500 chars):")
            print("-" * 80)
            print(result.raw_bob_output[:500])
            print("...")
            print("-" * 80)
    
    print("\nTest completed.")


if __name__ == "__main__":
    main()

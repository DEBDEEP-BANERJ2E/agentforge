"""
Groq Runner for Agent Generation.

This module uses GroqCloud API for agent generation instead of Bob Shell CLI
or watsonx.ai (which requires IBM Cloud provisioning permissions).

Architecture:
    User Prompt → Groq API → Generated Code → Validation → AgentGenerationResult
    
Benefits:
    - No IBM Cloud provisioning needed
    - Very fast inference (Groq's LPU architecture)
    - Generous free tier
    - OpenAI-compatible API
    - Simple setup
"""

import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from groq import Groq

from models import AgentGenerationResult, ToolFile
from parsers import extract_yaml_block, extract_python_files, extract_requirements
from validators import validate_agent_yaml, validate_python_file


def get_groq_client() -> Groq:
    """
    Create and return a Groq API client.
    
    Requires environment variable:
        - GROQ_API_KEY: Get from https://console.groq.com/keys
    
    Returns:
        Configured Groq client instance
        
    Raises:
        ValueError: If GROQ_API_KEY is missing
    """
    api_key = os.environ.get('GROQ_API_KEY')
    
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is required. "
            "Get your API key from: https://console.groq.com/keys"
        )
    
    return Groq(api_key=api_key)


def generate_with_groq(
    prompt: str, 
    model: str = "llama-3.3-70b-versatile"
) -> tuple[str, str]:
    """
    Generate agent code using Groq API.
    
    Args:
        prompt: The complete prompt including architect instructions
        model: Model to use (default: llama-3.3-70b-versatile)
               Options:
               - llama-3.3-70b-versatile (best for structured output)
               - deepseek-r1-distill-llama-70b (strong reasoning)
               - mixtral-8x7b-32768 (good balance)
               - llama3-8b-8192 (fastest)
        
    Returns:
        Tuple of (generated_text, session_id)
        
    Raises:
        Exception: If API call fails
    """
    client = get_groq_client()
    
    # Create chat completion
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert at generating watsonx Orchestrate ADK agents. "
                          "You output ONLY code blocks (YAML, Python, requirements.txt) with NO extra prose."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,  # Lower for more deterministic output
        max_tokens=4000,
        top_p=0.9,
        stream=False
    )
    
    generated_text = response.choices[0].message.content
    
    # Generate session ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = f"groq_{timestamp}"
    
    return generated_text, session_id


def save_session_output(session_id: str, output: str, script_dir: Path) -> None:
    """
    Save Groq output to a session file.
    
    Creates bob_sessions/ folder in repo root if it doesn't exist,
    and writes the raw output to bob_sessions/<session_id>.txt
    
    Args:
        session_id: The session identifier
        output: The output content to save
        script_dir: Path to the backend directory
    """
    # Go one level up from backend/ to get repo root
    repo_root = script_dir.parent
    sessions_dir = repo_root / "bob_sessions"
    
    # Create directory if it doesn't exist
    sessions_dir.mkdir(exist_ok=True)
    
    # Write session output
    session_file = sessions_dir / f"{session_id}.txt"
    try:
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(f"# Groq Generation Session\n")
            f.write(f"# Session ID: {session_id}\n")
            f.write(f"# Timestamp: {datetime.now().isoformat()}\n\n")
            f.write(output)
    except Exception as e:
        # Don't fail the whole process if we can't save the session
        print(f"Warning: Failed to save session output: {str(e)}")


def generate_agent(user_prompt: str, max_retries: int = 2) -> AgentGenerationResult:
    """
    Generate a watsonx Orchestrate ADK agent using Groq API.
    
    This function orchestrates the entire agent generation process:
    1. Loads the architect prompt template
    2. Calls Groq API to generate the agent
    3. Parses the output (YAML, Python files, requirements)
    4. Validates all components
    5. Retries with error feedback if validation fails
    
    Args:
        user_prompt: The user's description of the agent to generate
        max_retries: Maximum number of retry attempts if validation fails (default: 2)
        
    Returns:
        AgentGenerationResult with status and generated components
        
    Status codes:
        - "ok": Generation and validation successful
        - "timeout": API call timed out
        - "api_error": Groq API call failed
        - "validation_failed": Validation failed after all retries
        - "prompt_error": Failed to load prompt template
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    prompt_file = script_dir / "prompts" / "architect_prompt.txt"
    
    # Read the prompt template
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except FileNotFoundError:
        return AgentGenerationResult(
            status="prompt_error",
            agent_yaml=None,
            tools=[],
            requirements_txt=None,
            raw_bob_output="",
            bob_session_id="",
            errors=[f"Prompt template not found at {prompt_file}"]
        )
    except Exception as e:
        return AgentGenerationResult(
            status="prompt_error",
            agent_yaml=None,
            tools=[],
            requirements_txt=None,
            raw_bob_output="",
            bob_session_id="",
            errors=[f"Failed to read prompt template: {str(e)}"]
        )
    
    # Replace placeholder with user prompt
    prompt = prompt_template.replace("{USER_PROMPT}", user_prompt)
    
    # Check for required environment variables
    try:
        get_groq_client()
    except ValueError as e:
        return AgentGenerationResult(
            status="api_error",
            agent_yaml=None,
            tools=[],
            requirements_txt=None,
            raw_bob_output="",
            bob_session_id="",
            errors=[str(e)]
        )
    
    # Retry loop
    accumulated_errors = []
    
    for attempt in range(max_retries + 1):
        # If this is a retry, append error feedback to the prompt
        if attempt > 0 and accumulated_errors:
            error_feedback = "\n\nPREVIOUS ATTEMPT HAD ERRORS - PLEASE FIX:\n"
            error_feedback += "\n".join(f"- {error}" for error in accumulated_errors)
            error_feedback += "\n\nPlease regenerate the complete agent fixing these issues.\n"
            current_prompt = prompt + error_feedback
        else:
            current_prompt = prompt
        
        # Call Groq API
        try:
            generated_text, session_id = generate_with_groq(current_prompt)
            
            # Save session output
            save_session_output(session_id, generated_text, script_dir)
            
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return AgentGenerationResult(
                    status="timeout",
                    agent_yaml=None,
                    tools=[],
                    requirements_txt=None,
                    raw_bob_output="",
                    bob_session_id="",
                    errors=["Groq API call timed out"]
                )
            else:
                return AgentGenerationResult(
                    status="api_error",
                    agent_yaml=None,
                    tools=[],
                    requirements_txt=None,
                    raw_bob_output="",
                    bob_session_id="",
                    errors=[f"Groq API error: {error_msg}"]
                )
        
        # Parse the output
        agent_yaml = extract_yaml_block(generated_text)
        python_files_dict = extract_python_files(generated_text)
        requirements_txt = extract_requirements(generated_text)
        
        # Validate the parsed content
        validation_errors = []
        
        # Validate YAML
        if agent_yaml:
            yaml_errors = validate_agent_yaml(agent_yaml)
            validation_errors.extend(yaml_errors)
        else:
            validation_errors.append("No YAML configuration block found in output")
        
        # Validate Python files
        if not python_files_dict:
            validation_errors.append("No Python tool files found in output")
        else:
            for filename, code in python_files_dict.items():
                file_errors = validate_python_file(filename, code)
                if file_errors:
                    validation_errors.extend([f"{filename}: {err}" for err in file_errors])
        
        # Check requirements
        if not requirements_txt:
            validation_errors.append("No requirements.txt block found in output")
        
        # If validation passed, return success
        if not validation_errors:
            # Convert python files dict to list of ToolFile objects
            tools = [
                ToolFile(filename=filename, content=code)
                for filename, code in python_files_dict.items()
            ]
            
            return AgentGenerationResult(
                status="ok",
                agent_yaml=agent_yaml,
                tools=tools,
                requirements_txt=requirements_txt,
                raw_bob_output=generated_text,
                bob_session_id=session_id,
                errors=[]
            )
        
        # If validation failed, accumulate errors for retry
        accumulated_errors = validation_errors
        
        # If this was the last attempt, return validation_failed
        if attempt == max_retries:
            # Convert python files dict to list of ToolFile objects (even if invalid)
            tools = [
                ToolFile(filename=filename, content=code)
                for filename, code in python_files_dict.items()
            ]
            
            return AgentGenerationResult(
                status="validation_failed",
                agent_yaml=agent_yaml,
                tools=tools,
                requirements_txt=requirements_txt,
                raw_bob_output=generated_text,
                bob_session_id=session_id,
                errors=validation_errors
            )
    
    # This should never be reached, but just in case
    return AgentGenerationResult(
        status="validation_failed",
        agent_yaml=None,
        tools=[],
        requirements_txt=None,
        raw_bob_output="",
        bob_session_id="",
        errors=["Unexpected error in retry loop"]
    )

# Made with Bob

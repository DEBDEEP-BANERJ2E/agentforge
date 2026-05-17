"""
LLM Runner for Agent Generation.

Uses an OpenAI-compatible endpoint (configurable via .env) to generate
watsonx Orchestrate ADK agents from plain-English prompts.

Configure via environment variables:
    LLM_API_KEY   — API key for the LLM provider
    LLM_BASE_URL  — Base URL of the OpenAI-compatible API
    LLM_MODEL     — Model ID in provider format (e.g. opencode-go/kimi-k2.6)
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

from openai import OpenAI

from models import AgentGenerationResult, ToolFile
from parsers import extract_yaml_block, extract_python_files, extract_requirements
from validators import validate_agent_yaml, validate_python_file
from catalog_tools import get_catalog_tools, get_relevant_tools, format_tools_for_prompt


def get_llm_client() -> OpenAI:
    api_key = os.environ.get('LLM_API_KEY')
    base_url = os.environ.get('LLM_BASE_URL', 'https://opencode.ai/zen/go/v1')

    if not api_key:
        raise ValueError(
            "LLM_API_KEY environment variable is required. "
            "Set it in your .env file."
        )

    return OpenAI(api_key=api_key, base_url=base_url)


def generate_with_llm(prompt: str) -> tuple[str, str]:
    """
    Generate agent code using the configured LLM.

    Args:
        prompt: The complete architect prompt with user request injected.

    Returns:
        Tuple of (generated_text, session_id)
    """
    client = get_llm_client()
    model = os.environ.get('LLM_MODEL', 'opencode-go/kimi-k2.6')

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert at generating watsonx Orchestrate ADK agents. "
                    "Output ONLY the requested code blocks (YAML, Python, requirements.txt). "
                    "No prose, no explanations, no markdown outside of fenced code blocks."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=4000,
    )

    generated_text = response.choices[0].message.content

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = f"llm_{timestamp}"

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
    
    # Fetch available catalog tools and inject into prompt
    all_catalog_tools = []
    try:
        all_catalog_tools = get_catalog_tools(use_cache=True)
        relevant_tools = get_relevant_tools(user_prompt, all_catalog_tools, max_tools=15)
        tools_text = format_tools_for_prompt(relevant_tools, max_tools=15)
    except Exception as e:
        # If catalog discovery fails, continue without it
        print(f"Warning: Failed to discover catalog tools: {str(e)}")
        tools_text = "No catalog tools available (discovery failed)."
    
    prompt = (
        prompt_template
        .replace("{USER_PROMPT}", user_prompt)
        .replace("{AVAILABLE_TOOLS}", tools_text)
    )

    # Check for required environment variables
    try:
        get_llm_client()
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
        
        # Call LLM
        try:
            generated_text, session_id = generate_with_llm(current_prompt)
            
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
                    errors=[f"LLM API error: {error_msg}"]
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
        
        # Determine which tools in the YAML are catalog (already deployed) vs new
        yaml_tool_names: set[str] = set()
        if agent_yaml:
            try:
                _parsed = yaml.safe_load(agent_yaml)
                yaml_tool_names = set(_parsed.get("tools", []))
            except Exception:
                pass

        new_tool_names = {f[:-3] for f in python_files_dict}  # strip .py
        available_tool_names = {tool.name for tool in all_catalog_tools}
        catalog_tool_names = yaml_tool_names & available_tool_names  # already deployed
        missing_tools = yaml_tool_names - new_tool_names - catalog_tool_names

        # Validate Python files — only required for tools not in catalog
        if not python_files_dict and not catalog_tool_names:
            validation_errors.append("No Python tool files found in output")
        else:
            for filename, code in python_files_dict.items():
                file_errors = validate_python_file(filename, code)
                if file_errors:
                    validation_errors.extend([f"{filename}: {err}" for err in file_errors])
        if missing_tools:
            validation_errors.append(
                f"Tools referenced in YAML but not found in catalog or generated: {', '.join(missing_tools)}"
            )
        
        # Check requirements
        if not requirements_txt:
            validation_errors.append("No requirements.txt block found in output")
        
        # If validation passed, return success
        if not validation_errors:
            # Only include tools that aren't already in the catalog
            tools = [
                ToolFile(filename=filename, content=code)
                for filename, code in python_files_dict.items()
                if filename[:-3] not in catalog_tool_names
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
            tools = [
                ToolFile(filename=filename, content=code)
                for filename, code in python_files_dict.items()
                if filename[:-3] not in catalog_tool_names
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

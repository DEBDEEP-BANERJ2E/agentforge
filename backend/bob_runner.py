"""
Bob Shell Runner for Agent Generation.

This module provides the main entry point for generating watsonx Orchestrate ADK agents
using Bob Shell with automatic validation and retry logic.
"""

import subprocess
import os
from pathlib import Path
from typing import Optional

from models import AgentGenerationResult, ToolFile
from parsers import extract_yaml_block, extract_python_files, extract_requirements
from validators import validate_agent_yaml, validate_python_file


def generate_agent(user_prompt: str, max_retries: int = 2) -> AgentGenerationResult:
    """
    Generate a watsonx Orchestrate ADK agent using Bob Shell.
    
    This function orchestrates the entire agent generation process:
    1. Loads the architect prompt template
    2. Calls Bob Shell to generate the agent
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
        - "timeout": Bob Shell execution timed out
        - "bob_error": Bob Shell subprocess failed
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
        
        # Call Bob Shell (using PowerShell to execute bob.ps1)
        bob_path = r"C:\Users\My Laptop\AppData\Roaming\npm\bob.ps1"
        try:
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", bob_path, 
                 "--chat-mode=code", "--hide-intermediary-output", "--yolo", current_prompt],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=script_dir
            )
            
            stdout = result.stdout
            stderr = result.stderr
            
            # Check if subprocess failed
            if result.returncode != 0:
                return AgentGenerationResult(
                    status="bob_error",
                    agent_yaml=None,
                    tools=[],
                    requirements_txt=None,
                    raw_bob_output=stdout,
                    bob_session_id="",
                    errors=[f"Bob Shell failed with exit code {result.returncode}", stderr]
                )
            
        except subprocess.TimeoutExpired:
            return AgentGenerationResult(
                status="timeout",
                agent_yaml=None,
                tools=[],
                requirements_txt=None,
                raw_bob_output="",
                bob_session_id="",
                errors=["Bob Shell execution timed out after 180 seconds"]
            )
        except FileNotFoundError:
            return AgentGenerationResult(
                status="bob_error",
                agent_yaml=None,
                tools=[],
                requirements_txt=None,
                raw_bob_output="",
                bob_session_id="",
                errors=["Bob Shell executable not found. Make sure 'bob' is in your PATH"]
            )
        except Exception as e:
            return AgentGenerationResult(
                status="bob_error",
                agent_yaml=None,
                tools=[],
                requirements_txt=None,
                raw_bob_output="",
                bob_session_id="",
                errors=[f"Failed to execute Bob Shell: {str(e)}"]
            )
        
        # Parse the output
        agent_yaml = extract_yaml_block(stdout)
        python_files_dict = extract_python_files(stdout)
        requirements_txt = extract_requirements(stdout)
        
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
                raw_bob_output=stdout,
                bob_session_id="",
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
                raw_bob_output=stdout,
                bob_session_id="",
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

"""
ADK Deployment Module for AgentForge.

This module takes validated agent generation results from bob_runner and deploys
them to watsonx Orchestrate using the ADK CLI. It handles:
- Writing generated files to disk
- Importing tools (one per file)
- Importing the agent YAML
- Returning deployment status and chat URL
"""

import os
import yaml
from pathlib import Path
from typing import Optional
import subprocess
from dotenv import load_dotenv

from models import AgentGenerationResult, DeploymentResult, ToolFile
from orchestrate_env import verify_orchestrate_setup, run_orchestrate_command

# Load environment variables from .env file
load_dotenv()


# Environment variable for deployment timeout (default 300 seconds = 5 minutes)
DEPLOYMENT_TIMEOUT = int(os.environ.get('WXO_AGENT_DEPLOYMENT_TIMEOUT', '300'))

# Base directory for generated agent files
GENERATED_AGENTS_DIR = Path(__file__).parent / "generated_agents"


def get_orchestrate_chat_url(agent_name: str = "", environment: str = "wx0-AWS") -> str:
    """
    Construct the Orchestrate agents management URL.

    Returns:
        URL to the agents management page in Orchestrate UI
    """
    service_url = os.environ.get('ORCHESTRATE_SERVICE_URL', '')

    if service_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(service_url)
            ui_domain = parsed.netloc.replace('api.', '')
            return f"https://{ui_domain}/build/manage#agents"
        except Exception:
            pass

    return "https://watson-orchestrate.cloud.ibm.com/build/manage#agents"


def write_agent_files(
    agent_name: str,
    agent_yaml: str,
    tools: list[ToolFile],
    requirements_txt: str
) -> Path:
    """
    Write generated agent files to disk in the generated_agents directory.
    
    Creates structure:
    generated_agents/
    └── <agent_name>/
        ├── agent.yaml
        ├── tools/
        │   ├── tool_one.py
        │   └── tool_two.py
        └── requirements.txt
    
    Args:
        agent_name: Name of the agent (used as directory name)
        agent_yaml: YAML configuration content
        tools: List of ToolFile objects
        requirements_txt: Requirements file content
        
    Returns:
        Path to the agent directory
        
    Raises:
        OSError: If file writing fails
    """
    # Create agent directory
    agent_dir = GENERATED_AGENTS_DIR / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    # Create tools subdirectory
    tools_dir = agent_dir / "tools"
    tools_dir.mkdir(exist_ok=True)
    
    # Write agent.yaml
    agent_yaml_path = agent_dir / "agent.yaml"
    with open(agent_yaml_path, 'w', encoding='utf-8') as f:
        f.write(agent_yaml)
    
    # Write each tool file
    for tool in tools:
        tool_path = tools_dir / tool.filename
        with open(tool_path, 'w', encoding='utf-8') as f:
            f.write(tool.content)
    
    # Write requirements.txt
    requirements_path = agent_dir / "requirements.txt"
    with open(requirements_path, 'w', encoding='utf-8') as f:
        f.write(requirements_txt)
    
    return agent_dir


def import_tool(
    tool_path: Path,
    requirements_path: Path,
    timeout: int = 60
) -> tuple[bool, str, str]:
    """
    Import a single tool into Orchestrate.
    
    Runs: orchestrate tools import -k python -f <tool.py> -r <requirements.txt>
    
    Args:
        tool_path: Path to the Python tool file
        requirements_path: Path to requirements.txt
        timeout: Command timeout in seconds
        
    Returns:
        Tuple of (success: bool, stdout: str, stderr: str)
    """
    try:
        result = run_orchestrate_command(
            [
                'tools', 'import',
                '-k', 'python',
                '-f', str(tool_path),
                '-r', str(requirements_path)
            ],
            timeout=timeout,
            check_env=False  # Already checked in deploy_agent
        )
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        return False, "", f"Tool import timed out after {timeout} seconds"
    except Exception as e:
        return False, "", f"Tool import failed: {str(e)}"


def import_agent(agent_yaml_path: Path, timeout: int = 60) -> tuple[bool, str, str]:
    """
    Import an agent into Orchestrate.
    
    Runs: orchestrate agents import -f <agent.yaml>
    
    Args:
        agent_yaml_path: Path to the agent YAML file
        timeout: Command timeout in seconds
        
    Returns:
        Tuple of (success: bool, stdout: str, stderr: str)
    """
    try:
        result = run_orchestrate_command(
            ['agents', 'import', '-f', str(agent_yaml_path)],
            timeout=timeout,
            check_env=False  # Already checked in deploy_agent
        )
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        return False, "", f"Agent import timed out after {timeout} seconds"
    except Exception as e:
        return False, "", f"Agent import failed: {str(e)}"


def parse_tool_import_errors(stderr: str, stdout: str) -> list[str]:
    """
    Parse tool import errors to provide helpful error messages.
    
    Common errors:
    - Package not in allowlist
    - Invalid tool syntax
    - Missing dependencies
    
    Args:
        stderr: Standard error output
        stdout: Standard output
        
    Returns:
        List of parsed error messages
    """
    errors = []
    combined = (stderr + "\n" + stdout).lower()
    
    if 'not in allowlist' in combined or 'not allowed' in combined:
        errors.append(
            "Package not in tenant allowlist. Only use approved packages: "
            "httpx, requests, pydantic, pandas, numpy"
        )
    
    if 'syntax error' in combined:
        errors.append("Python syntax error in tool file")
    
    if 'import error' in combined or 'modulenotfounderror' in combined:
        errors.append("Missing required imports in tool file")
    
    if 'invalid tool' in combined:
        errors.append("Tool does not meet ADK requirements (missing @tool decorator or async def)")
    
    if not errors:
        # If we couldn't parse specific errors, return the raw stderr
        errors.append(stderr or stdout or "Unknown tool import error")
    
    return errors


def parse_agent_import_errors(stderr: str, stdout: str) -> list[str]:
    """
    Parse agent import errors to provide helpful error messages.
    
    Common errors:
    - Invalid YAML schema
    - Missing required fields
    - Invalid agent name
    
    Args:
        stderr: Standard error output
        stdout: Standard output
        
    Returns:
        List of parsed error messages
    """
    errors = []
    combined = (stderr + "\n" + stdout).lower()
    
    if 'schema' in combined or 'validation' in combined:
        errors.append("Agent YAML does not match required schema")
    
    if 'name' in combined and 'invalid' in combined:
        errors.append("Invalid agent name (must be alphanumeric + underscores only)")
    
    if 'missing' in combined and 'field' in combined:
        errors.append("Missing required fields in agent YAML")
    
    if 'tool' in combined and 'not found' in combined:
        errors.append("Agent references tools that were not imported")
    
    if not errors:
        # If we couldn't parse specific errors, return the raw stderr
        errors.append(stderr or stdout or "Unknown agent import error")
    
    return errors


def deploy_agent(generation_result: AgentGenerationResult) -> DeploymentResult:
    """
    Deploy a generated agent to watsonx Orchestrate.
    
    This is the main entry point for the deployment pipeline. It:
    1. Verifies Orchestrate environment is ready
    2. Writes generated files to disk
    3. Imports each tool (one at a time)
    4. Imports the agent YAML
    5. Returns deployment status and chat URL
    
    Args:
        generation_result: Output from bob_runner.generate_agent()
        
    Returns:
        DeploymentResult with deployment status, chat URL, and any errors
    """
    # Initialize result tracking
    cli_output_parts = []
    errors = []
    tools_imported = []
    
    # Extract agent name from YAML
    try:
        agent_data = yaml.safe_load(generation_result.agent_yaml)
        agent_name = agent_data.get('name', 'unknown_agent')
    except Exception as e:
        return DeploymentResult(
            agent_name="unknown",
            chat_url="",
            tools_imported=[],
            status="agent_import_failed",
            cli_output="",
            errors=[f"Failed to parse agent YAML: {str(e)}"]
        )
    
    # Step 1: Verify environment
    cli_output_parts.append("=== Environment Verification ===")
    env_ok, env_errors = verify_orchestrate_setup()
    if not env_ok:
        return DeploymentResult(
            agent_name=agent_name,
            chat_url="",
            tools_imported=[],
            status="auth_failed",
            cli_output="\n".join(cli_output_parts),
            errors=env_errors
        )
    cli_output_parts.append("✓ Environment verified")
    
    # Step 2: Write files to disk
    cli_output_parts.append("\n=== Writing Files ===")
    try:
        agent_dir = write_agent_files(
            agent_name=agent_name,
            agent_yaml=generation_result.agent_yaml,
            tools=generation_result.tools,
            requirements_txt=generation_result.requirements_txt
        )
        cli_output_parts.append(f"✓ Files written to {agent_dir}")
    except Exception as e:
        return DeploymentResult(
            agent_name=agent_name,
            chat_url="",
            tools_imported=[],
            status="tool_import_failed",
            cli_output="\n".join(cli_output_parts),
            errors=[f"Failed to write files: {str(e)}"]
        )
    
    # Step 3: Import tools (one at a time)
    cli_output_parts.append("\n=== Importing Tools ===")
    tools_dir = agent_dir / "tools"
    requirements_path = agent_dir / "requirements.txt"
    
    for tool in generation_result.tools:
        tool_path = tools_dir / tool.filename
        cli_output_parts.append(f"\nImporting {tool.filename}...")
        
        success, stdout, stderr = import_tool(
            tool_path=tool_path,
            requirements_path=requirements_path,
            timeout=DEPLOYMENT_TIMEOUT
        )
        
        cli_output_parts.append(f"STDOUT: {stdout}")
        if stderr:
            cli_output_parts.append(f"STDERR: {stderr}")
        
        if success:
            # Extract tool name (filename without .py)
            tool_name = tool.filename[:-3] if tool.filename.endswith('.py') else tool.filename
            tools_imported.append(tool_name)
            cli_output_parts.append(f"✓ {tool.filename} imported successfully")
        else:
            # Parse and collect errors
            tool_errors = parse_tool_import_errors(stderr, stdout)
            errors.extend([f"{tool.filename}: {err}" for err in tool_errors])
            cli_output_parts.append(f"✗ {tool.filename} import failed")
    
    # If any tool imports failed, return early
    if errors:
        return DeploymentResult(
            agent_name=agent_name,
            chat_url="",
            tools_imported=tools_imported,
            status="tool_import_failed",
            cli_output="\n".join(cli_output_parts),
            errors=errors
        )
    
    # Step 4: Import agent
    cli_output_parts.append("\n=== Importing Agent ===")
    agent_yaml_path = agent_dir / "agent.yaml"
    
    success, stdout, stderr = import_agent(
        agent_yaml_path=agent_yaml_path,
        timeout=DEPLOYMENT_TIMEOUT
    )
    
    cli_output_parts.append(f"STDOUT: {stdout}")
    if stderr:
        cli_output_parts.append(f"STDERR: {stderr}")
    
    if not success:
        agent_errors = parse_agent_import_errors(stderr, stdout)
        return DeploymentResult(
            agent_name=agent_name,
            chat_url="",
            tools_imported=tools_imported,
            status="agent_import_failed",
            cli_output="\n".join(cli_output_parts),
            errors=agent_errors
        )
    
    cli_output_parts.append(f"✓ Agent '{agent_name}' imported successfully")
    
    # Step 5: Generate chat URL
    chat_url = get_orchestrate_chat_url(agent_name)
    
    # Success!
    return DeploymentResult(
        agent_name=agent_name,
        chat_url=chat_url,
        tools_imported=tools_imported,
        status="deployed",
        cli_output="\n".join(cli_output_parts),
        errors=[]
    )

# Made with Bob

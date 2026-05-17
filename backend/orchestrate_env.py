"""
Environment verification and activation utilities for watsonx Orchestrate ADK.

This module ensures that the Conda environment is properly activated and that
the Orchestrate CLI is accessible before attempting any deployment operations.
"""

import subprocess
import shutil
import os
from typing import Tuple, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_conda_prefix() -> Optional[str]:
    """
    Get the Conda installation prefix.
    
    Checks for Conda in common locations:
    1. CONDA_EXE environment variable
    2. ~/miniconda3
    3. ~/anaconda3
    4. /opt/conda
    
    Returns:
        Path to Conda prefix, or None if not found
    """
    # Check CONDA_EXE environment variable
    conda_exe = os.environ.get('CONDA_EXE')
    if conda_exe:
        # CONDA_EXE points to conda binary, get parent directories
        conda_path = Path(conda_exe).parent.parent
        return str(conda_path)
    
    # Check common installation locations
    home = Path.home()
    common_locations = [
        home / "miniconda3",
        home / "anaconda3",
        Path("/opt/conda"),
    ]
    
    for location in common_locations:
        if location.exists() and (location / "bin" / "conda").exists():
            return str(location)
    
    return None


def is_conda_env_active() -> bool:
    """
    Check if the watsonx Conda environment is currently active.
    
    Returns:
        True if watsonx environment is active, False otherwise
    """
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    return conda_env == 'watsonx'


def verify_orchestrate_cli() -> Tuple[bool, str]:
    """
    Verify that the Orchestrate CLI is accessible.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Check if orchestrate is on PATH
    orchestrate_path = shutil.which('orchestrate')
    if not orchestrate_path:
        return False, "Orchestrate CLI not found on PATH. Ensure Conda environment 'watsonx' is activated."
    
    # Try to run orchestrate --version to verify it works
    try:
        result = subprocess.run(
            ['orchestrate', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return True, f"Orchestrate CLI found at {orchestrate_path}"
        else:
            return False, f"Orchestrate CLI found but failed to execute: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return False, "Orchestrate CLI timed out during verification"
    except Exception as e:
        return False, f"Failed to verify Orchestrate CLI: {str(e)}"


def verify_orchestrate_auth() -> Tuple[bool, str]:
    """
    Verify that Orchestrate authentication is configured.
    
    Attempts to list agents to check if auth is valid.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            ['orchestrate', 'agents', 'list'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check for common auth error patterns
        stderr_lower = result.stderr.lower()
        stdout_lower = result.stdout.lower()
        
        if 'unauthorized' in stderr_lower or 'unauthorized' in stdout_lower:
            return False, "Authentication failed. Run: orchestrate env activate wx0-AWS"
        
        if 'no active environment' in stderr_lower or 'no active environment' in stdout_lower:
            return False, "No active Orchestrate environment. Run: orchestrate env activate wx0-AWS"
        
        if 'token' in stderr_lower and 'expired' in stderr_lower:
            return False, "API token expired. Run: orchestrate env activate wx0-AWS"
        
        if result.returncode == 0:
            return True, "Orchestrate authentication verified"
        
        # If we got here, there's some other error
        return False, f"Orchestrate auth check failed: {result.stderr or result.stdout}"
    
    except subprocess.TimeoutExpired:
        return False, "Orchestrate auth check timed out"
    except Exception as e:
        return False, f"Failed to verify Orchestrate auth: {str(e)}"


def verify_orchestrate_setup() -> Tuple[bool, list[str]]:
    """
    Comprehensive verification of Orchestrate deployment prerequisites.
    
    Checks:
    1. Conda environment is active
    2. Orchestrate CLI is accessible
    3. Authentication is valid
    
    Returns:
        Tuple of (success: bool, errors: list[str])
    """
    errors = []
    
    # Check 1: Conda environment
    if not is_conda_env_active():
        conda_prefix = get_conda_prefix()
        if conda_prefix:
            errors.append(
                f"Conda environment 'watsonx' is not active. "
                f"Run: conda activate watsonx"
            )
        else:
            errors.append(
                "Conda not found. Install Miniconda/Anaconda and create environment: "
                "conda env create -f backend/environment.yml"
            )
        # If conda env is not active, other checks will likely fail
        return False, errors
    
    # Check 2: Orchestrate CLI
    cli_ok, cli_msg = verify_orchestrate_cli()
    if not cli_ok:
        errors.append(cli_msg)
        # If CLI is not available, auth check will fail
        return False, errors
    
    # Check 3: Authentication
    auth_ok, auth_msg = verify_orchestrate_auth()
    if not auth_ok:
        errors.append(auth_msg)
        return False, errors
    
    return True, []


def get_conda_activation_prefix() -> str:
    """
    Get the shell command prefix needed to activate Conda environment.
    
    Returns:
        Shell command string to source Conda and activate watsonx env
    """
    conda_prefix = get_conda_prefix()
    if not conda_prefix:
        raise RuntimeError("Conda installation not found")
    
    # Return bash command to source conda and activate environment
    return f"source {conda_prefix}/etc/profile.d/conda.sh && conda activate watsonx"


def run_orchestrate_command(
    args: list[str],
    timeout: int = 60,
    check_env: bool = True
) -> subprocess.CompletedProcess:
    """
    Run an Orchestrate CLI command with proper environment activation.
    
    Args:
        args: Command arguments (e.g., ['agents', 'list'])
        timeout: Command timeout in seconds
        check_env: Whether to verify environment before running
        
    Returns:
        CompletedProcess object with stdout, stderr, returncode
        
    Raises:
        RuntimeError: If environment verification fails
        subprocess.TimeoutExpired: If command times out
    """
    if check_env:
        ok, errors = verify_orchestrate_setup()
        if not ok:
            raise RuntimeError(f"Environment verification failed: {'; '.join(errors)}")
    
    # Build full command
    cmd = ['orchestrate'] + args
    
    # Run command
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    return result

# Made with Bob

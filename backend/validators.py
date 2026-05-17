"""
Validators for agent YAML configurations and Python tool files.

This module provides validation functions to ensure generated agents
meet the required specifications and naming conventions.
"""

import ast
import re
from typing import List
import yaml


def validate_agent_yaml(yaml_str: str) -> List[str]:
    """
    Validate agent YAML configuration.
    
    Checks that the YAML contains all required fields and that the name
    field follows naming conventions (alphanumeric and underscores only).
    
    Required fields:
    - spec_version
    - kind
    - name
    - description
    - llm
    - style
    - instructions
    - tools
    
    Args:
        yaml_str: The YAML configuration as a string
        
    Returns:
        List of error messages. Empty list if validation passes.
        
    Example:
        >>> yaml_str = "name: my_agent\\ndescription: test"
        >>> errors = validate_agent_yaml(yaml_str)
        >>> len(errors) > 0
        True
    """
    errors = []
    
    # Try to parse YAML
    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {str(e)}")
        return errors
    
    if not isinstance(data, dict):
        errors.append("YAML must be a dictionary/object")
        return errors
    
    # Check required fields
    required_fields = ['spec_version', 'kind', 'name', 'description', 'llm', 'style', 'instructions', 'tools']
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            errors.append(f"Field '{field}' cannot be empty")
    
    # Validate specific field values
    if 'spec_version' in data and data['spec_version'] != 'v1':
        errors.append(f"spec_version must be 'v1', got '{data['spec_version']}'")
    
    if 'kind' in data and data['kind'] != 'native':
        errors.append(f"kind must be 'native', got '{data['kind']}'")
    
    if 'style' in data and data['style'] != 'default':
        errors.append(f"style must be 'default', got '{data['style']}'")
    
    if 'llm' in data and data['llm'] != 'watsonx/meta-llama/llama-3-2-90b-vision-instruct':
        errors.append(f"llm must be 'watsonx/meta-llama/llama-3-2-90b-vision-instruct', got '{data['llm']}'")
    
    # Validate tools is a list
    if 'tools' in data and not isinstance(data['tools'], list):
        errors.append(f"tools must be a list, got {type(data['tools']).__name__}")
    
    # Validate name field format (alphanumeric and underscores only)
    if 'name' in data and data['name']:
        name = str(data['name'])
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            errors.append(
                f"Invalid name '{name}': must contain only alphanumeric characters and underscores"
            )
    
    return errors


def validate_python_file(filename: str, code: str) -> List[str]:
    """
    Validate Python tool file.
    
    Checks that:
    1. Filename is alphanumeric plus underscores and ends with .py
    2. Code contains exactly one @tool decorator
    3. Code passes Python syntax validation (ast.parse)
    4. Function is async def (not just def)
    5. Code imports httpx
    6. Code does NOT import requests
    7. Code imports from ibm_watsonx_orchestrate.agent_builder.tools
    
    Args:
        filename: The name of the Python file
        code: The Python code as a string
        
    Returns:
        List of error messages. Empty list if validation passes.
        
    Example:
        >>> validate_python_file("my_tool.py", "@tool\\ndef my_func(): pass")
        []
        >>> validate_python_file("my-tool.py", "invalid code")
        ['Invalid filename...', ...]
    """
    errors = []
    
    # Validate filename format
    if not filename.endswith('.py'):
        errors.append(f"Filename '{filename}' must end with .py")
    
    # Check filename contains only alphanumeric and underscores
    name_without_ext = filename[:-3] if filename.endswith('.py') else filename
    if not re.match(r'^[a-zA-Z0-9_]+$', name_without_ext):
        errors.append(
            f"Invalid filename '{filename}': must contain only alphanumeric characters and underscores (plus .py extension)"
        )
    
    # Check for exactly one @tool decorator
    tool_decorator_pattern = r'@tool\b'
    tool_matches = re.findall(tool_decorator_pattern, code)
    
    if len(tool_matches) == 0:
        errors.append("Code must contain at least one @tool decorator")
    elif len(tool_matches) > 1:
        errors.append(f"Code must contain exactly one @tool decorator, found {len(tool_matches)}")
    
    # Check for async def
    async_def_pattern = r'async\s+def\s+\w+'
    if not re.search(async_def_pattern, code):
        errors.append("Function must be defined as 'async def', not just 'def'")
    
    # Check for urllib.request import (required; httpx/requests are not available in runtime)
    if not re.search(r'import\s+urllib\.request', code):
        errors.append("Code must include 'import urllib.request'")

    # Check that requests/httpx are NOT imported (not available in the runtime)
    if re.search(r'import\s+requests|from\s+requests\s+import', code):
        errors.append("Code must NOT import 'requests' — use 'urllib.request' instead")
    if re.search(r'import\s+httpx|from\s+httpx\s+import', code):
        errors.append("Code must NOT import 'httpx' — use 'urllib.request' instead")
    
    # Check for ibm_watsonx_orchestrate import
    ibm_import_pattern = r'from\s+ibm_watsonx_orchestrate\.agent_builder\.tools\s+import\s+tool'
    if not re.search(ibm_import_pattern, code):
        errors.append("Code must include 'from ibm_watsonx_orchestrate.agent_builder.tools import tool'")
    
    # Validate Python syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append(f"Python syntax error: {str(e)} at line {e.lineno}")
    except Exception as e:
        errors.append(f"Failed to parse Python code: {str(e)}")
    
    return errors
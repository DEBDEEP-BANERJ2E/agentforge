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
    - instructions
    
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
    required_fields = ['spec_version', 'kind', 'name', 'description', 'llm', 'instructions']
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            errors.append(f"Field '{field}' cannot be empty")
    
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
    
    # Validate Python syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append(f"Python syntax error: {str(e)} at line {e.lineno}")
    except Exception as e:
        errors.append(f"Failed to parse Python code: {str(e)}")
    
    return errors

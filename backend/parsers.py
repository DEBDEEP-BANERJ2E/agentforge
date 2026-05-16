"""
Parsers for extracting structured content from LLM responses.

This module provides functions to parse YAML configurations, Python code files,
and requirements from fenced code blocks in text responses.
"""

import re
from typing import Dict, Optional


def extract_yaml_block(text: str) -> Optional[str]:
    """
    Extract content from a YAML fenced code block.
    
    Searches for content within ```yaml ... ``` or ```yml ... ``` blocks.
    
    Args:
        text: The text containing the YAML code block
        
    Returns:
        The YAML content as a string, or None if not found
        
    Example:
        >>> text = "Some text\\n```yaml\\nkey: value\\n```\\nMore text"
        >>> extract_yaml_block(text)
        'key: value'
    """
    # Pattern to match ```yaml or ```yml blocks
    pattern = r'```(?:yaml|yml)\s*\n(.*?)```'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return None


def extract_python_files(text: str) -> Dict[str, str]:
    """
    Extract Python code files from fenced code blocks with filename comments.
    
    Searches for ```python blocks where the VERY FIRST LINE matches exactly:
    # filename: <name>.py
    where <name> is alphanumeric + underscores only.
    
    Does NOT accept loose forms like "# tool_name.py" without "filename:" prefix.
    
    Args:
        text: The text containing Python code blocks
        
    Returns:
        Dictionary mapping filenames to their code content.
        Returns empty dict if no valid Python files are found.
        
    Example:
        >>> text = "```python\\n# filename: test.py\\nprint('hello')\\n```"
        >>> extract_python_files(text)
        {'test.py': "print('hello')"}
    """
    python_files = {}
    
    # Pattern to match ```python blocks
    pattern = r'```python\s*\n(.*?)```'
    matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        code_block = match.group(1)
        lines = code_block.split('\n')
        
        if not lines:
            continue
            
        # Check if first line matches EXACTLY: # filename: <name>.py
        first_line = lines[0].strip()
        
        # Only accept the strict pattern with "filename:" prefix
        filename_pattern = r'^#\s*filename:\s*([a-zA-Z0-9_]+\.py)\s*$'
        filename_match = re.match(filename_pattern, first_line)
        
        if filename_match:
            filename = filename_match.group(1)
            # Get the rest of the code (excluding the filename comment)
            code_content = '\n'.join(lines[1:]).strip()
            python_files[filename] = code_content
    
    return python_files


def extract_requirements(text: str) -> Optional[str]:
    """
    Extract content from a requirements.txt fenced code block.
    
    Searches for content within ```txt or ```text blocks where the VERY FIRST LINE
    is exactly: # filename: requirements.txt
    
    Does NOT accept loose forms like "# requirements.txt" without "filename:" prefix.
    
    Args:
        text: The text containing the requirements code block
        
    Returns:
        The requirements content as a string, or None if not found or sentinel missing
        
    Example:
        >>> text = "```txt\\n# filename: requirements.txt\\nrequests>=2.0.0\\n```"
        >>> extract_requirements(text)
        'requests>=2.0.0'
    """
    # Pattern to match ```txt or ```text blocks
    pattern = r'```(?:txt|text)\s*\n(.*?)```'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        content = match.group(1)
        lines = content.split('\n')
        
        if not lines:
            return None
        
        # Check if first line matches EXACTLY: # filename: requirements.txt
        first_line = lines[0].strip()
        sentinel_pattern = r'^#\s*filename:\s*requirements\.txt\s*$'
        
        if re.match(sentinel_pattern, first_line):
            # Return the rest of the content (excluding the sentinel line)
            return '\n'.join(lines[1:]).strip()
    
    return None
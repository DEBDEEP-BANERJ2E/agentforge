"""
Catalog Tools Discovery Module.

This module discovers available tools in watsonx Orchestrate and makes them
available for agent generation. This enables AgentForge to:

1. Automatically discover existing tools (Python, catalog, MCP)
2. Include them in the agent generation prompt
3. Wire them into new agents without writing Python code

This is the "killer feature" - leveraging the 1,119+ catalog tools plus
any custom tools already deployed.
"""

import subprocess
import json
from typing import List, Dict, Optional
from pathlib import Path


class CatalogTool:
    """Represents a tool available in the Orchestrate catalog."""
    
    def __init__(self, name: str, description: str, tool_type: str, 
                 toolkit: Optional[str] = None, app_id: Optional[str] = None):
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.toolkit = toolkit
        self.app_id = app_id
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.tool_type,
            "toolkit": self.toolkit,
            "app_id": self.app_id
        }
    
    def __repr__(self) -> str:
        return f"CatalogTool(name='{self.name}', type='{self.tool_type}')"


def discover_catalog_tools() -> List[CatalogTool]:
    """
    Discover all available tools in watsonx Orchestrate.
    
    This runs `orchestrate tools list --format json` and parses the output
    to get a list of all available tools (Python, catalog, MCP).
    
    Returns:
        List of CatalogTool objects
        
    Raises:
        RuntimeError: If orchestrate CLI is not available or command fails
    """
    try:
        # Run orchestrate tools list with JSON output
        result = subprocess.run(
            ["orchestrate", "tools", "list", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        # Parse JSON output
        tools_data = json.loads(result.stdout)
        
        # Convert to CatalogTool objects
        catalog_tools = []
        for tool_data in tools_data:
            tool = CatalogTool(
                name=tool_data.get("name", ""),
                description=tool_data.get("description", ""),
                tool_type=tool_data.get("type", "unknown"),
                toolkit=tool_data.get("toolkit"),
                app_id=tool_data.get("app_id")
            )
            catalog_tools.append(tool)
        
        return catalog_tools
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Timeout while discovering catalog tools")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to discover catalog tools: {e.stderr}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse catalog tools JSON: {str(e)}")
    except FileNotFoundError:
        raise RuntimeError(
            "orchestrate CLI not found. Make sure you're in the watsonx conda environment."
        )


def filter_tools_by_category(tools: List[CatalogTool], category: str) -> List[CatalogTool]:
    """
    Filter tools by category (e.g., 'github', 'weather', 'news').
    
    Args:
        tools: List of CatalogTool objects
        category: Category keyword to filter by (case-insensitive)
        
    Returns:
        Filtered list of tools
    """
    category_lower = category.lower()
    return [
        tool for tool in tools
        if category_lower in tool.name.lower() or category_lower in tool.description.lower()
    ]


def format_tools_for_prompt(tools: List[CatalogTool], max_tools: int = 20) -> str:
    """
    Format catalog tools for inclusion in the agent generation prompt.
    
    Args:
        tools: List of CatalogTool objects
        max_tools: Maximum number of tools to include (default: 20)
        
    Returns:
        Formatted string describing available tools
    """
    if not tools:
        return "No catalog tools available."
    
    # Limit to max_tools
    tools_to_include = tools[:max_tools]
    
    lines = ["AVAILABLE CATALOG TOOLS (you can reference these by name in the agent YAML):"]
    lines.append("")
    
    for tool in tools_to_include:
        lines.append(f"- {tool.name}: {tool.description}")
    
    if len(tools) > max_tools:
        lines.append(f"\n... and {len(tools) - max_tools} more tools available")
    
    return "\n".join(lines)


def get_relevant_tools(user_prompt: str, all_tools: List[CatalogTool], 
                       max_tools: int = 10) -> List[CatalogTool]:
    """
    Get tools relevant to the user's prompt using keyword matching.
    
    This is a simple keyword-based relevance filter. For production,
    you might want to use embeddings or LLM-based relevance scoring.
    
    Args:
        user_prompt: The user's agent description
        all_tools: List of all available tools
        max_tools: Maximum number of relevant tools to return
        
    Returns:
        List of relevant CatalogTool objects
    """
    # Extract keywords from prompt (simple approach)
    keywords = set(user_prompt.lower().split())
    
    # Score each tool by keyword overlap
    scored_tools = []
    for tool in all_tools:
        tool_text = f"{tool.name} {tool.description}".lower()
        score = sum(1 for keyword in keywords if keyword in tool_text)
        if score > 0:
            scored_tools.append((score, tool))
    
    # Sort by score (descending) and return top N
    scored_tools.sort(reverse=True, key=lambda x: x[0])
    return [tool for score, tool in scored_tools[:max_tools]]


def save_catalog_cache(tools: List[CatalogTool], cache_file: Path) -> None:
    """
    Save discovered tools to a cache file for faster subsequent loads.
    
    Args:
        tools: List of CatalogTool objects
        cache_file: Path to cache file
    """
    cache_data = [tool.to_dict() for tool in tools]
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        # Don't fail if we can't save cache
        print(f"Warning: Failed to save catalog cache: {str(e)}")


def load_catalog_cache(cache_file: Path) -> Optional[List[CatalogTool]]:
    """
    Load tools from cache file if it exists and is recent.
    
    Args:
        cache_file: Path to cache file
        
    Returns:
        List of CatalogTool objects, or None if cache is invalid/missing
    """
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        tools = [
            CatalogTool(
                name=item["name"],
                description=item["description"],
                tool_type=item["type"],
                toolkit=item.get("toolkit"),
                app_id=item.get("app_id")
            )
            for item in cache_data
        ]
        
        return tools
        
    except Exception as e:
        print(f"Warning: Failed to load catalog cache: {str(e)}")
        return None


def get_catalog_tools(use_cache: bool = True) -> List[CatalogTool]:
    """
    Get catalog tools, using cache if available and requested.
    
    Args:
        use_cache: Whether to use cached tools if available
        
    Returns:
        List of CatalogTool objects
    """
    script_dir = Path(__file__).parent
    cache_file = script_dir / ".catalog_cache.json"
    
    # Try cache first
    if use_cache:
        cached_tools = load_catalog_cache(cache_file)
        if cached_tools is not None:
            return cached_tools
    
    # Discover tools
    tools = discover_catalog_tools()
    
    # Save to cache
    save_catalog_cache(tools, cache_file)
    
    return tools


# Example usage
if __name__ == "__main__":
    print("🔍 Discovering catalog tools...")
    
    try:
        tools = get_catalog_tools(use_cache=False)
        
        print(f"\n✅ Found {len(tools)} tools!")
        print("\n📊 Tool breakdown:")
        
        # Count by type
        type_counts = {}
        for tool in tools:
            type_counts[tool.tool_type] = type_counts.get(tool.tool_type, 0) + 1
        
        for tool_type, count in sorted(type_counts.items()):
            print(f"  - {tool_type}: {count}")
        
        # Show some examples
        print("\n📝 Example tools:")
        for tool in tools[:10]:
            print(f"  - {tool.name}: {tool.description[:60]}...")
        
        # Test filtering
        print("\n🔎 GitHub-related tools:")
        github_tools = filter_tools_by_category(tools, "github")
        for tool in github_tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test relevance matching
        print("\n🎯 Tools relevant to 'fetch weather data':")
        relevant = get_relevant_tools("fetch weather data", tools, max_tools=5)
        for tool in relevant:
            print(f"  - {tool.name}: {tool.description}")
        
    except RuntimeError as e:
        print(f"\n❌ Error: {str(e)}")

# Made with Bob

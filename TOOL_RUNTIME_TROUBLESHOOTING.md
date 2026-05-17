# Tool Runtime Troubleshooting Guide

## 🔍 Common Tool Execution Errors

### Error: "Error getting Python tool status"

**Symptom:**
```
Tool: tool_name
Input: {"arg": ""}
Output: Error getting Python tool status
```

**Root Cause:**
The tool was generated with a generic `arg: str` parameter, but watsonx Orchestrate doesn't know what value to pass for this parameter.

**Why This Happens:**
When a tool is defined with parameters, Orchestrate needs to know:
1. What the parameter represents
2. What value to pass
3. How to extract that value from the user's request

A generic `arg` parameter provides no semantic meaning, so Orchestrate can't determine what to pass.

---

## ✅ Solution: Proper Tool Parameter Design

### Option 1: No Parameters (Recommended for Simple Tools)

For tools that don't need input (e.g., "fetch top stories", "get current time"):

```python
@tool
async def hacker_news_fetcher() -> dict:
    """Fetch top 5 Hacker News stories.
    
    Returns:
        A dictionary containing the top 5 Hacker News stories
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        top_stories = response.json()[:5]
        stories = []
        for story_id in top_stories:
            story_response = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
            story = story_response.json()
            stories.append({"title": story["title"], "url": story.get("url", "")})
        return {"stories": stories}
```

**When to use:**
- Tool performs a fixed action
- No user input needed
- Tool is self-contained

---

### Option 2: Explicit Named Parameters (For Tools Needing Input)

For tools that need user input:

```python
@tool
async def search_hacker_news(query: str, limit: int = 10) -> dict:
    """Search Hacker News for stories matching a query.
    
    Args:
        query: The search query string
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        A dictionary containing matching stories
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": query, "hitsPerPage": limit}
        )
        return response.json()
```

**When to use:**
- Tool needs user input
- Parameters have clear semantic meaning
- Orchestrate can extract values from user's request

---

## 🚫 Anti-Patterns to Avoid

### ❌ Generic `arg` Parameter

```python
# DON'T DO THIS
@tool
async def tool_name(arg: str) -> dict:
    """Tool description.
    Args:
        arg: Not used
    """
    # ...
```

**Problems:**
- No semantic meaning
- Orchestrate can't determine what to pass
- Runtime error: "Error getting Python tool status"

---

### ❌ Unused Parameters

```python
# DON'T DO THIS
@tool
async def fetch_news(arg: str) -> dict:
    """Fetch news.
    Args:
        arg: Not used  # ← This is a red flag!
    """
    # arg is never used in the function body
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/news")
        return response.json()
```

**Fix:** Remove the parameter entirely if it's not used.

---

## 🔧 How to Fix Existing Broken Tools

### Step 1: Identify the Issue

Check the generated tool file in `backend/generated_agents/<agent_name>/tools/`:

```python
# If you see this pattern, it's broken:
@tool
async def tool_name(arg: str) -> dict:
    """..."""
    # arg is not used anywhere
```

### Step 2: Regenerate with Fixed Prompt

The prompt template has been updated in `backend/prompts/architect_prompt.txt` to generate tools without generic `arg` parameters.

Simply regenerate the agent:
1. Go to http://localhost:3000
2. Enter the same prompt again
3. The new agent will be generated correctly

### Step 3: Verify the Fix

Check the new tool file:

```python
# Should look like this:
@tool
async def tool_name() -> dict:
    """..."""
    # No parameters if not needed
```

Or if parameters are needed:

```python
@tool
async def tool_name(query: str, limit: int = 10) -> dict:
    """...
    Args:
        query: Specific description
        limit: Specific description
    """
    # Parameters are actually used
```

---

## 📊 Debugging Checklist

When a tool fails at runtime:

- [ ] Check tool definition in `backend/generated_agents/<agent_name>/tools/`
- [ ] Verify parameters have semantic meaning (not generic `arg`)
- [ ] Confirm parameters are actually used in function body
- [ ] Check if tool needs parameters at all
- [ ] Review Orchestrate error message for clues
- [ ] Test tool locally before deploying

---

## 🎯 Best Practices

### 1. Design Tools with Clear Intent

**Good:**
```python
@tool
async def get_weather(city: str, units: str = "metric") -> dict:
    """Get weather for a specific city."""
```

**Bad:**
```python
@tool
async def get_data(arg: str) -> dict:
    """Get some data."""
```

### 2. Use Type Hints

Always include type hints for parameters and return values:

```python
@tool
async def search(query: str, max_results: int = 10) -> dict:
    """Search with type hints."""
```

### 3. Document Parameters Clearly

Use Google-style docstrings:

```python
@tool
async def tool_name(param1: str, param2: int = 10) -> dict:
    """One-line summary.
    
    Longer description if needed.
    
    Args:
        param1: Clear description of what this parameter does
        param2: Clear description with default value explanation
    
    Returns:
        Clear description of return value structure
    """
```

### 4. Test Tools Independently

Before deploying, test the tool function directly:

```python
import asyncio

async def test_tool():
    result = await tool_name()
    print(result)

asyncio.run(test_tool())
```

---

## 🔍 Advanced Debugging

### View Deployed Tool in Orchestrate

1. Go to IBM Cloud Orchestrate UI
2. Navigate to **Tools** section
3. Find your tool by name
4. Click to view definition
5. Check the **Input Schema** section

The input schema should match your function parameters.

### Check Tool Import Logs

When deploying, check the backend logs:

```bash
# In terminal where backend is running
# Look for lines like:
Importing tool: tool_name.py
Tool import successful: tool_name
```

If import fails, the error message will indicate the issue.

---

## 📚 Related Documentation

- [ADK Tool Development Guide](https://developer.watson-orchestrate.ibm.com/tools/create_tool)
- [Python Tool Best Practices](https://developer.watson-orchestrate.ibm.com/tools/python_tools)
- [Agent Builder Documentation](https://developer.watson-orchestrate.ibm.com/agents/overview)

---

## 🆘 Still Having Issues?

If you've followed this guide and still encounter errors:

1. **Check the generated files:**
   ```bash
   ls -la backend/generated_agents/<agent_name>/tools/
   cat backend/generated_agents/<agent_name>/tools/<tool_name>.py
   ```

2. **Review the agent YAML:**
   ```bash
   cat backend/generated_agents/<agent_name>/agent.yaml
   ```

3. **Check backend logs:**
   Look for validation errors or deployment failures

4. **Test Groq generation:**
   ```bash
   cd backend
   python test_groq_connection.py
   ```

5. **Regenerate the agent:**
   Sometimes a fresh generation with the updated prompt fixes everything

---

## 📝 Summary

**Key Takeaway:** Tools should either have NO parameters (for simple actions) or EXPLICIT, MEANINGFUL parameters (for actions requiring input). Never use generic `arg` parameters.

**Quick Fix:** The prompt template has been updated. Simply regenerate your agent to get working tools.

**Prevention:** The updated prompt template in `backend/prompts/architect_prompt.txt` now generates tools correctly by default.
# Contributing to AgentForge

Thank you for your interest in contributing! AgentForge is a tool for generating and deploying IBM watsonx Orchestrate agents from plain-English prompts.

## Getting Started

1. **Fork** the repository and clone your fork
2. **Set up the environment:**
   ```bash
   conda env create -f backend/environment.yml
   conda activate watsonx
   ```
3. **Set up environment variables** by copying `.env.example` to `.env` and filling in your credentials
4. **Start the backend:**
   ```bash
   cd api && python main.py
   ```
5. **Start the frontend:**
   ```bash
   cd frontend && npm install && npm run dev
   ```

## How to Contribute

### Reporting Bugs

Open an issue using the **Bug Report** template. Include:
- Steps to reproduce
- Expected vs actual behavior
- Error messages or screenshots
- Your environment (OS, Python version, Node version)

### Suggesting Features

Open an issue using the **Feature Request** template. Describe:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you considered

### Submitting Code

1. Create a branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Make your changes following the guidelines below
3. Test your changes locally
4. Open a pull request using the PR template

## Code Guidelines

### Backend (Python)

- Python 3.12+
- Follow PEP 8 style
- Tool files must use `urllib.request` only — no `httpx` or `requests`
- Every `@tool` function must be `async def` and return `-> dict`
- Always use `.get()` for external API dict access

### Frontend (TypeScript / Next.js)

- Follow the existing component structure in `frontend/app/`
- Use Tailwind CSS for styling
- No new external dependencies without discussion

### Prompt Engineering

- Changes to `backend/prompts/architect_prompt.txt` should be tested against all three example prompts (weather+air quality, crypto+currency, GitHub PRs)
- Add a reference example if introducing a new API pattern

## Commit Messages

Use conventional commits:
```
feat: add new tool type
fix: correct air quality API URL
docs: update setup guide
refactor: simplify validator logic
```

## Questions?

Open a [Discussion](../../discussions) or file an issue — we're happy to help.

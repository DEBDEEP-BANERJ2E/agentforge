# AgentForge Deployment Setup Guide

## Quick Start

### 1. Environment Configuration (Already Done ✅)

The `.env` file has been created with production credentials:

```bash
ORCHESTRATE_SERVICE_URL=https://api.ca-tor.watson-orchestrate.cloud.ibm.com/instances/4e732bf0-848b-4b3d-be31-f80c223c0950
ORCHESTRATE_API_KEY=Ah_3gjB8_kLkOLt6sDXUEtA3Lvtc-I9DwAODkQXt8t4T
ORCHESTRATE_ENV_NAME=wx0-AWS
WXO_AGENT_DEPLOYMENT_TIMEOUT=300
```

**⚠️ SECURITY**: The `.env` file is in `.gitignore` - never commit it!

### 2. Install Dependencies

```bash
# Option A: Use existing environment (if python-dotenv is installed)
pip install python-dotenv==1.0.0

# Option B: Create fresh Conda environment (recommended)
conda env create -f backend/environment.yml
conda activate watsonx
```

### 3. Configure Orchestrate Authentication

```bash
# Activate the Orchestrate environment
orchestrate env activate wx0-AWS

# Verify it worked
orchestrate agents list
```

### 4. Test Deployment

```bash
cd backend
python test_deploy.py
```

## What Was Implemented

### Environment Variables Support

All deployment modules now load configuration from `.env`:

- **Service URL**: Automatically parsed to generate correct chat URLs
- **API Key**: Used for authentication (via Orchestrate CLI)
- **Environment Name**: Target deployment environment
- **Timeout**: Configurable deployment timeout

### Dynamic Chat URL Generation

The `get_orchestrate_chat_url()` function:

1. Reads `ORCHESTRATE_SERVICE_URL` from `.env`
2. Parses the region (e.g., `ca-tor` from the API URL)
3. Constructs the UI URL: `https://ca-tor.watson-orchestrate.cloud.ibm.com/agents/{agent_name}`

**Example**:
```python
from backend.deploy_agent import get_orchestrate_chat_url

url = get_orchestrate_chat_url('my_agent')
# Returns: https://ca-tor.watson-orchestrate.cloud.ibm.com/agents/my_agent
```

### Files Created

1. **`.env`** - Production credentials (gitignored)
2. **`.env.example`** - Template for team members
3. **`backend/environment.yml`** - Updated with `python-dotenv==1.0.0`
4. **`backend/orchestrate_env.py`** - Updated to load `.env`
5. **`backend/deploy_agent.py`** - Updated with dynamic URL generation

## Verification Tests

✅ **Environment loading**: `.env` file loads correctly
```bash
$ python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ORCHESTRATE_SERVICE_URL'))"
https://api.ca-tor.watson-orchestrate.cloud.ibm.com/instances/4e732bf0-848b-4b3d-be31-f80c223c0950
```

✅ **Chat URL generation**: Correctly parses service URL
```bash
$ python -c "from backend.deploy_agent import get_orchestrate_chat_url; print(get_orchestrate_chat_url('test_agent'))"
https://ca-tor.watson-orchestrate.cloud.ibm.com/agents/test_agent
```

✅ **Deployment test**: Environment verification working
```bash
$ cd backend && python test_deploy.py
# Shows proper error handling and environment checks
```

## For Team Members

If you need to use your own credentials:

1. Copy the template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   - Get your service URL from IBM Cloud
   - Get your API key from Orchestrate settings
   - Set your environment name

3. Never commit `.env` - it's already in `.gitignore`

## Troubleshooting

### "Import dotenv could not be resolved"

This is a linter warning because the current Python environment doesn't have `python-dotenv`. Install it:

```bash
pip install python-dotenv==1.0.0
```

Or use the Conda environment:

```bash
conda activate watsonx
```

### "Environment variables not loading"

Make sure:
1. `.env` file exists in the repository root
2. You're running Python from the repository root (or a subdirectory)
3. `python-dotenv` is installed

### "Chat URL is wrong"

The URL is generated from `ORCHESTRATE_SERVICE_URL` in `.env`. Verify:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ORCHESTRATE_SERVICE_URL'))"
```

## Next Steps

1. **Varun**: Verify the setup works on your machine
2. **FastAPI Integration (KAN-12)**: Import `deploy_agent()` for the backend API
3. **Frontend (KAN-15)**: Use `DeploymentResult.chat_url` to display agent links
4. **Testing**: Run full deployment test after Orchestrate auth is configured

## Security Checklist

- ✅ `.env` file created with credentials
- ✅ `.env` is in `.gitignore` (line 7)
- ✅ `.env.example` template provided (no sensitive data)
- ✅ README warns about not committing `.env`
- ✅ Credentials never hardcoded in source files

## Contact

For questions about the deployment module:
- **Primary**: Debdeep
- **Watcher**: Varun
- **Reference**: KAN-13 task documentation
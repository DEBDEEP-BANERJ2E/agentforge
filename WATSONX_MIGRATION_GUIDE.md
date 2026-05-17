# watsonx.ai Migration Guide

## Overview

AgentForge has been migrated from Bob Shell CLI (which is not publicly available) to **watsonx.ai API** for agent generation. This provides a more stable, production-ready architecture.

## What Changed

### Before (Bob Shell CLI)
```
User Prompt → FastAPI → bob -p "..." → Parse Output → Deploy
```

### After (watsonx.ai API)
```
User Prompt → FastAPI → watsonx.ai API → Parse Output → Deploy
```

## Architecture Changes

| Component | Old | New | Status |
|-----------|-----|-----|--------|
| Generation Engine | `bob_runner.py` (Bob Shell CLI) | `watsonx_runner.py` (watsonx.ai API) | ✅ Complete |
| Data Models | `models.py` | `models.py` (updated with new status codes) | ✅ Complete |
| Environment | `environment.yml` | `environment.yml` (added watsonx.ai SDK) | ✅ Complete |
| Configuration | `.env` | `.env` (added watsonx.ai credentials) | ✅ Complete |
| API Routes | `api/routes.py` | `api/routes.py` (updated import) | ✅ Complete |

## Why This Change?

### Problem
The Bob Shell CLI (`bob`) referenced in the original architecture is **not publicly available**:
- `which bob` → not found
- `brew install ibm-bob` → no package exists
- `bobide --help` → only shows IDE commands, no `-p` flag for non-interactive execution
- `bobide -p "hello"` → "Warning: 'p' is not in the list of known options"

### Solution
Use **watsonx.ai API** directly:
- ✅ Publicly available with free tier
- ✅ 300,000 free tokens/month
- ✅ Access to IBM Granite + other models
- ✅ Production-ready REST API
- ✅ Better error handling and observability

## Setup Instructions

### 1. Get watsonx.ai Credentials

#### A. Get IBM Cloud API Key
1. Go to: https://cloud.ibm.com/iam/apikeys
2. Click "Create"
3. Name it "AgentForge watsonx.ai"
4. Copy the API key (you'll need it for both `WATSONX_API_KEY` and `ORCHESTRATE_API_KEY`)

#### B. Create watsonx.ai Project
1. Go to: https://dataplatform.cloud.ibm.com/projects
2. Click "New project"
3. Choose "Create an empty project"
4. Name it "AgentForge"
5. After creation, click on "Manage" tab
6. Copy the "Project ID" from the URL or project settings

### 2. Update Environment Variables

Edit your `.env` file:

```bash
# watsonx Orchestrate (existing)
ORCHESTRATE_SERVICE_URL=https://api.ca-tor.watson-orchestrate.cloud.ibm.com/instances/YOUR_INSTANCE_ID
ORCHESTRATE_API_KEY=your_ibm_cloud_api_key
ORCHESTRATE_ENV_NAME=wx0-AWS

# watsonx.ai (NEW - required for agent generation)
WATSONX_API_KEY=your_ibm_cloud_api_key  # Same as ORCHESTRATE_API_KEY
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### 3. Update Conda Environment

```bash
# Remove old environment
conda deactivate
conda env remove -n watsonx

# Create new environment with watsonx.ai SDK
conda env create -f backend/environment.yml

# Activate
conda activate watsonx

# Verify watsonx.ai SDK is installed
python -c "from ibm_watsonx_ai import APIClient; print('✅ watsonx.ai SDK installed')"
```

### 4. Test watsonx.ai Connection

```bash
cd backend
python -c "
from watsonx_runner import get_watsonx_client
try:
    client = get_watsonx_client()
    print('✅ watsonx.ai connection successful')
    print(f'Project ID: {client.default_project_id}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### 5. Start the System

```bash
# Terminal 1: Backend
conda activate watsonx
orchestrate env activate wx0-AWS
./start_api.sh

# Terminal 2: Frontend
cd frontend
npm install  # First time only
npm run dev
```

### 6. Test Agent Generation

1. Open http://localhost:3000
2. Type: "Create an agent that fetches top 5 Hacker News stories"
3. Click "Generate Agent"
4. Watch real-time progress (now powered by watsonx.ai!)

## Technical Details

### New Dependencies

Added to `backend/environment.yml`:
```yaml
- ibm-watsonx-ai==1.1.0
- ibm-cloud-sdk-core==3.20.0
```

### New Status Codes

`AgentGenerationResult.status` now includes:
- `"ok"` - Success
- `"validation_failed"` - Validation failed after retries
- `"api_error"` - watsonx.ai API call failed (NEW)
- `"prompt_error"` - Failed to load prompt template (NEW)
- `"timeout"` - API call timed out
- `"bob_error"` - Legacy status (kept for backward compatibility)

### Model Selection

Default model: `ibm/granite-3-8b-instruct`

Why Granite 3?
- ✅ Optimized for structured output (YAML, code)
- ✅ Fast inference
- ✅ Good at following instructions
- ✅ Available on free tier

Alternative models you can try:
- `ibm/granite-3-2-8b-instruct` - Smaller, faster
- `meta-llama/llama-3-2-90b-vision-instruct` - More powerful
- `mistralai/mistral-large` - Strong reasoning

To change model, edit `backend/watsonx_runner.py`:
```python
def generate_with_watsonx(prompt: str, model_id: str = "your-model-id"):
```

### Generation Parameters

Configured for deterministic structured output:
```python
parameters = {
    GenParams.MAX_NEW_TOKENS: 4000,
    GenParams.TEMPERATURE: 0.3,  # Lower = more deterministic
    GenParams.TOP_P: 0.9,
    GenParams.TOP_K: 50,
    GenParams.REPETITION_PENALTY: 1.1,
}
```

## Troubleshooting

### Error: "WATSONX_API_KEY environment variable is required"

**Solution**: Add watsonx.ai credentials to `.env`:
```bash
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_project_id
```

### Error: "Import 'ibm_watsonx_ai' could not be resolved"

**Solution**: Reinstall environment:
```bash
conda deactivate
conda env remove -n watsonx
conda env create -f backend/environment.yml
conda activate watsonx
```

### Error: "Project not found"

**Solution**: Verify project ID:
1. Go to https://dataplatform.cloud.ibm.com/projects
2. Click on your project
3. Copy Project ID from URL or settings
4. Update `WATSONX_PROJECT_ID` in `.env`

### Error: "Authentication failed"

**Solution**: Verify API key:
1. Go to https://cloud.ibm.com/iam/apikeys
2. Verify key is active
3. Try creating a new key
4. Update both `WATSONX_API_KEY` and `ORCHESTRATE_API_KEY` in `.env`

### Generation Quality Issues

If generated agents have validation errors:

1. **Adjust temperature**: Lower = more deterministic
   ```python
   GenParams.TEMPERATURE: 0.2  # Try 0.1-0.5
   ```

2. **Try different model**:
   ```python
   model_id="ibm/granite-3-2-8b-instruct"  # Smaller, faster
   ```

3. **Increase max retries**:
   ```python
   generate_agent(prompt, max_retries=3)  # Default is 2
   ```

## Cost Considerations

### Free Tier Limits
- **300,000 tokens/month** (approximately 225,000 words)
- **~20 compute hours/month**

### Typical Usage
- **1 agent generation**: ~2,000-4,000 tokens
- **75-150 agents/month** on free tier

### Monitoring Usage
1. Go to: https://dataplatform.cloud.ibm.com/projects
2. Click on your project
3. View "Usage" tab

## Migration Checklist

- [x] Create `backend/watsonx_runner.py`
- [x] Update `backend/models.py` with new status codes
- [x] Update `backend/environment.yml` with watsonx.ai SDK
- [x] Update `.env.example` with watsonx.ai configuration
- [x] Update `api/routes.py` to use `watsonx_runner`
- [ ] Get watsonx.ai credentials
- [ ] Update `.env` with credentials
- [ ] Reinstall Conda environment
- [ ] Test watsonx.ai connection
- [ ] Test agent generation end-to-end

## Benefits of This Architecture

1. **No Hidden Dependencies**: Everything is publicly available
2. **Production-Ready**: watsonx.ai is IBM's production AI platform
3. **Better Observability**: API calls are logged and traceable
4. **Cost-Effective**: Free tier is generous for development/demos
5. **Scalable**: Easy to upgrade to paid tier for production
6. **Enterprise-Grade**: Built on IBM Cloud infrastructure

## Support

- **watsonx.ai Docs**: https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-overview.html
- **watsonx.ai SDK**: https://ibm.github.io/watsonx-ai-python-sdk/
- **IBM Cloud Support**: https://cloud.ibm.com/unifiedsupport/supportcenter

## Next Steps

1. Complete the migration checklist above
2. Test agent generation with watsonx.ai
3. Deploy to production with confidence!

**The system is now more stable, transparent, and production-ready!** 🎉
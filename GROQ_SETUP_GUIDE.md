# GroqCloud Setup Guide - AgentForge

## 🎯 Why Groq?

GroqCloud is the **recommended** LLM provider for AgentForge because:

✅ **No IBM Cloud Provisioning** - Works immediately, no permission issues
✅ **Generous Free Tier** - Plenty for development and demos
✅ **Extremely Fast** - Groq's LPU architecture is blazing fast
✅ **Simple Setup** - Just one API key, no project creation
✅ **Great Models** - Llama 3.3 70B, DeepSeek R1, Mixtral, and more
✅ **OpenAI-Compatible** - Familiar API structure

## 🚀 Quick Start (5 Minutes)

### 1. Get Groq API Key

1. Go to: https://console.groq.com/keys
2. Sign up (free, instant)
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add:
GROQ_API_KEY=gsk_your_actual_key_here

# Keep your existing Orchestrate config:
ORCHESTRATE_SERVICE_URL=https://api.ca-tor.watson-orchestrate.cloud.ibm.com/instances/YOUR_INSTANCE_ID
ORCHESTRATE_API_KEY=your_orchestrate_api_key
ORCHESTRATE_ENV_NAME=wx0-AWS
```

### 3. Install Dependencies

```bash
# Remove old environment
conda deactivate
conda env remove -n watsonx

# Create new environment with Groq SDK
conda env create -f backend/environment.yml
conda activate watsonx

# Verify Groq SDK is installed
python -c "from groq import Groq; print('✅ Groq SDK installed')"
```

### 4. Test Groq Connection

```bash
cd backend
python -c "
from groq_runner import get_groq_client
try:
    client = get_groq_client()
    print('✅ Groq connection successful')
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

### 6. Generate Your First Agent

1. Open http://localhost:3000
2. Type: "Create an agent that fetches top 5 Hacker News stories"
3. Click "Generate Agent"
4. Watch real-time progress (powered by Groq!)
5. Agent deploys to watsonx Orchestrate

**🎉 You're done! Agent generation now works without IBM Cloud provisioning!**

## 📊 Available Models

| Model | Best For | Speed | Quality |
|-------|----------|-------|---------|
| `llama-3.3-70b-versatile` | **Structured output** (YAML, code) | Fast | Excellent |
| `deepseek-r1-distill-llama-70b` | Reasoning, complex tasks | Fast | Excellent |
| `mixtral-8x7b-32768` | Balanced performance | Very Fast | Good |
| `llama3-8b-8192` | Quick iterations | Blazing Fast | Good |

**Default**: `llama-3.3-70b-versatile` (best for generating ADK agents)

### Changing Models

Edit `backend/groq_runner.py`:

```python
def generate_with_groq(
    prompt: str, 
    model: str = "deepseek-r1-distill-llama-70b"  # Change here
) -> tuple[str, str]:
```

## 💰 Free Tier Limits

### Groq Free Tier
- **Requests per minute**: 30
- **Requests per day**: 14,400
- **Tokens per minute**: 6,000

### Typical Usage
- **1 agent generation**: ~2,000-4,000 tokens
- **~100-200 agents/day** on free tier

**More than enough for development, demos, and hackathons!**

## 🔧 Configuration

### Environment Variables

```bash
# Required
GROQ_API_KEY=gsk_your_key_here

# Optional (for watsonx Orchestrate deployment)
ORCHESTRATE_SERVICE_URL=...
ORCHESTRATE_API_KEY=...
ORCHESTRATE_ENV_NAME=wx0-AWS
```

### Generation Parameters

In `backend/groq_runner.py`:

```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    temperature=0.3,      # Lower = more deterministic (0.0-2.0)
    max_tokens=4000,      # Maximum response length
    top_p=0.9,           # Nucleus sampling (0.0-1.0)
    stream=False         # Set True for streaming responses
)
```

**Recommended for agent generation:**
- `temperature`: 0.2-0.4 (more deterministic)
- `max_tokens`: 4000 (enough for YAML + tools)
- `top_p`: 0.9 (good balance)

## 🐛 Troubleshooting

### Error: "GROQ_API_KEY environment variable is required"

**Solution**: Add API key to `.env`:
```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

### Error: "Import 'groq' could not be resolved"

**Solution**: Reinstall environment:
```bash
conda deactivate
conda env remove -n watsonx
conda env create -f backend/environment.yml
conda activate watsonx
```

### Error: "Rate limit exceeded"

**Solution**: You hit the free tier limit. Options:
1. Wait a minute (30 requests/minute limit)
2. Upgrade to paid tier (very affordable)
3. Use a different model (some have higher limits)

### Error: "Invalid API key"

**Solution**: 
1. Verify key starts with `gsk_`
2. Check for extra spaces in `.env`
3. Generate a new key at https://console.groq.com/keys

### Generation Quality Issues

If generated agents have validation errors:

1. **Lower temperature**:
   ```python
   temperature=0.2  # More deterministic
   ```

2. **Try different model**:
   ```python
   model="deepseek-r1-distill-llama-70b"  # Better reasoning
   ```

3. **Increase max retries**:
   ```python
   generate_agent(prompt, max_retries=3)  # Default is 2
   ```

## 📈 Monitoring Usage

### Check Usage
1. Go to: https://console.groq.com/usage
2. View requests, tokens, and rate limits
3. Monitor daily/monthly usage

### Upgrade if Needed
- **Pay-as-you-go**: $0.05-0.27 per million tokens
- **No monthly fees**
- **Much cheaper than OpenAI**

## 🔄 Switching Between Providers

AgentForge supports multiple LLM providers. To switch:

### Use Groq (Current - Recommended)
```python
# In api/routes.py
from groq_runner import generate_agent
```

### Use watsonx.ai (Requires IBM Cloud provisioning)
```python
# In api/routes.py
from watsonx_runner import generate_agent
```

### Use Bob Shell (Not publicly available)
```python
# In api/routes.py
from bob_runner import generate_agent
```

**All runners have the same interface**, so switching is just changing one import!

## 🎯 Architecture

```
User Prompt
    ↓
FastAPI Backend
    ↓
groq_runner.py
    ↓
Groq API (Llama 3.3 70B)
    ↓
Generated YAML + Tools
    ↓
Validation
    ↓
deploy_agent.py
    ↓
watsonx Orchestrate
    ↓
Live Agent!
```

## 📚 Additional Resources

- **Groq Console**: https://console.groq.com
- **Groq Documentation**: https://console.groq.com/docs
- **API Reference**: https://console.groq.com/docs/api-reference
- **Model Benchmarks**: https://wow.groq.com/

## 🎓 Best Practices

### 1. Use Appropriate Models
- **Structured output** (YAML, code): `llama-3.3-70b-versatile`
- **Reasoning tasks**: `deepseek-r1-distill-llama-70b`
- **Quick iterations**: `llama3-8b-8192`

### 2. Optimize Temperature
- **Deterministic output**: 0.2-0.3
- **Creative output**: 0.7-0.9
- **Agent generation**: 0.3 (default)

### 3. Handle Rate Limits
- Implement exponential backoff
- Cache successful generations
- Use appropriate retry logic (already built-in)

### 4. Monitor Costs
- Track token usage
- Set up alerts in Groq console
- Optimize prompts to reduce tokens

## ✅ Advantages Over watsonx.ai

| Aspect | Groq | watsonx.ai |
|--------|------|------------|
| **Setup** | ✅ Instant | ❌ Requires provisioning |
| **Permissions** | ✅ None needed | ❌ Editor role required |
| **Speed** | ✅ Extremely fast | ⚠️ Moderate |
| **Free Tier** | ✅ Generous | ✅ Good |
| **API Simplicity** | ✅ Very simple | ⚠️ More complex |
| **IBM Integration** | ⚠️ None | ✅ Native |

**For hackathons and development, Groq is the clear winner!**

## 🚀 Next Steps

1. ✅ Get Groq API key
2. ✅ Update `.env`
3. ✅ Reinstall Conda environment
4. ✅ Test connection
5. ✅ Generate your first agent
6. 🎉 Deploy to watsonx Orchestrate

**You're ready to build AI agents at lightning speed!** ⚡
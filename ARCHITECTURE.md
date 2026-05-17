# AgentForge Architecture Documentation

## 🎯 Project Vision

**"Vercel for AI Agents"** - Type one sentence, get a deployed watsonx Orchestrate agent in ~90 seconds.

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│  "Create an agent that summarizes Hacker News every morning"        │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js) - KAN-15                       │
│  ┌─────────────────┐  ┌──────────────────────────────────────────┐ │
│  │  Chat Input UI  │  │  Real-time Progress Display              │ │
│  │  - Text input   │  │  ✓ Understanding...                      │ │
│  │  - Submit btn   │  │  ✓ Generating agent...                   │ │
│  └─────────────────┘  │  ✓ Validating...                         │ │
│                       │  ✓ Importing tools...                    │ │
│                       │  ✓ Deploying agent...                    │ │
│                       │  ✓ Ready! [Open Chat]                    │ │
│                       └──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓ HTTP POST /generate-agent
┌─────────────────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Orchestrator) - KAN-12                 │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  POST /generate-agent                                           ││
│  │  - Receives user prompt                                         ││
│  │  - Calls bob_runner.generate_agent()                            ││
│  │  - Calls deploy_agent.deploy_agent()                            ││
│  │  - Streams progress via Server-Sent Events (SSE)                ││
│  │  - Returns DeploymentResult with chat URL                       ││
│  └─────────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  GET /status/{task_id}                                          ││
│  │  - Returns current generation/deployment status                 ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│           BOB RUNNER (AI Generation Layer) - KAN-11 ✅               │
│  File: backend/bob_runner.py                                         │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  generate_agent(prompt: str) -> AgentGenerationResult           ││
│  │                                                                  ││
│  │  1. Load architect_prompt.txt template                          ││
│  │  2. Inject user prompt                                          ││
│  │  3. Call Bob Shell with custom mode                             ││
│  │  4. Parse output (YAML, Python, requirements)                   ││
│  │  5. Validate against ADK schema                                 ││
│  │  6. Retry on errors (max 2 retries)                             ││
│  │  7. Save session to bob_sessions/                               ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  Dependencies:                                                        │
│  - parsers.py: Extract YAML/Python/requirements from Bob output      │
│  - validators.py: Validate agent YAML and tool files                 │
│  - models.py: AgentGenerationResult data contract                    │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓ AgentGenerationResult
┌─────────────────────────────────────────────────────────────────────┐
│         ADK DEPLOYMENT PIPELINE (Orchestrate Deploy) - KAN-13 ✅     │
│  File: backend/deploy_agent.py                                       │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  deploy_agent(result: AgentGenerationResult) -> DeploymentResult││
│  │                                                                  ││
│  │  1. Verify environment (orchestrate_env.py)                     ││
│  │     - Check Conda activation                                    ││
│  │     - Verify Orchestrate CLI                                    ││
│  │     - Validate authentication                                   ││
│  │                                                                  ││
│  │  2. Write files to disk                                         ││
│  │     generated_agents/<agent_name>/                              ││
│  │     ├── agent.yaml                                              ││
│  │     ├── tools/                                                  ││
│  │     │   ├── tool_one.py                                         ││
│  │     │   └── tool_two.py                                         ││
│  │     └── requirements.txt                                        ││
│  │                                                                  ││
│  │  3. Import tools (one at a time)                                ││
│  │     orchestrate tools import -k python -f tool.py -r req.txt    ││
│  │                                                                  ││
│  │  4. Import agent                                                ││
│  │     orchestrate agents import -f agent.yaml                     ││
│  │                                                                  ││
│  │  5. Generate chat URL from service URL                          ││
│  │     https://ca-tor.watson-orchestrate.cloud.ibm.com/agents/...  ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  Dependencies:                                                        │
│  - orchestrate_env.py: Environment verification                      │
│  - models.py: DeploymentResult data contract                         │
│  - .env: Service URL, API key, environment name                      │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓ DeploymentResult
┌─────────────────────────────────────────────────────────────────────┐
│            WATSONX ORCHESTRATE (IBM Cloud SaaS)                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  Agent Registry (Draft State)                                   ││
│  │  - Agent appears in Orchestrate UI                              ││
│  │  - Tools are registered and callable                            ││
│  │  - Accessible via chat interface                                ││
│  │  - Can be promoted to production with: orchestrate agents deploy││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         USER GETS CHAT URL                           │
│  https://ca-tor.watson-orchestrate.cloud.ibm.com/agents/my_agent    │
│  → Opens in browser → User can immediately chat with deployed agent  │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### 1. Data Contracts (models.py)

```python
# User Input
user_prompt: str = "Create an agent that..."

# Bob Runner Output
@dataclass
class AgentGenerationResult:
    agent_yaml: str              # ADK-compatible YAML
    tools: list[ToolFile]        # Python tool files
    requirements_txt: str        # Pinned dependencies
    raw_bob_output: str          # Full Bob stdout
    bob_session_id: str          # For hackathon submission
    status: Literal["ok", "validation_failed", "bob_error", "timeout"]
    errors: list[str]

# Deployment Output
@dataclass
class DeploymentResult:
    agent_name: str              # Name in Orchestrate
    chat_url: str                # Direct link to agent
    tools_imported: list[str]    # Successfully imported tools
    status: Literal["deployed", "tool_import_failed", "agent_import_failed", "auth_failed", "timeout"]
    cli_output: str              # Full CLI logs
    errors: list[str]
```

### 2. Pipeline Flow

```
User Prompt
    ↓
bob_runner.generate_agent(prompt)
    ↓
AgentGenerationResult
    ↓
deploy_agent.deploy_agent(result)
    ↓
DeploymentResult
    ↓
Chat URL returned to user
```

## 📁 Project Structure

```
agentforge/
├── backend/
│   ├── models.py                    # ✅ Data contracts (KAN-9)
│   ├── bob_runner.py                # ✅ Bob Shell wrapper (KAN-11)
│   ├── parsers.py                   # ✅ Extract YAML/Python/requirements (KAN-11)
│   ├── validators.py                # ✅ Validate ADK schema (KAN-11)
│   ├── orchestrate_env.py           # ✅ Environment verification (KAN-13)
│   ├── deploy_agent.py              # ✅ ADK deployment pipeline (KAN-13)
│   ├── test_runner.py               # ✅ Bob Runner tests (KAN-11)
│   ├── test_deploy.py               # ✅ Deployment tests (KAN-13)
│   ├── test_e2e_integration.py      # ✅ End-to-end integration test
│   ├── environment.yml              # ✅ Conda environment spec (KAN-13)
│   └── prompts/
│       └── architect_prompt.txt     # ✅ Bob prompt template (KAN-11)
│
├── bob_sessions/                    # ✅ Saved Bob task sessions
│   └── .gitkeep
│
├── generated_agents/                # ✅ Deployed agent files (created at runtime)
│   └── <agent_name>/
│       ├── agent.yaml
│       ├── tools/
│       │   └── *.py
│       └── requirements.txt
│
├── .env                             # ✅ Environment configuration (KAN-13)
├── .env.example                     # ✅ Template for team (KAN-13)
├── .gitignore                       # ✅ Protects credentials
├── README.md                        # ✅ Setup instructions
├── ARCHITECTURE.md                  # ✅ This file
└── DEPLOYMENT_SETUP.md              # ✅ Deployment guide

# TODO: Not yet implemented
├── api/                             # ❌ FastAPI backend (KAN-12)
│   ├── main.py                      # FastAPI app
│   ├── routes.py                    # API endpoints
│   └── sse.py                       # Server-Sent Events
│
└── frontend/                        # ❌ Next.js UI (KAN-15)
    ├── app/
    ├── components/
    └── lib/
```

## 🔧 Component Details

### ✅ Bob Runner (KAN-11) - COMPLETE

**Purpose**: Convert natural language → ADK artifacts

**Key Features**:
- Custom "Agent Architect" mode via `.bob/custom_modes.yaml`
- Strict output formatting (YAML + Python + requirements)
- Validation against ADK schema
- Automatic retry on errors (max 2 retries)
- Session export for hackathon submission

**Files**:
- `bob_runner.py`: Main orchestration
- `parsers.py`: Extract fenced code blocks
- `validators.py`: Schema validation
- `prompts/architect_prompt.txt`: Bob prompt template

### ✅ ADK Deployment (KAN-13) - COMPLETE

**Purpose**: Deploy generated artifacts → watsonx Orchestrate

**Key Features**:
- Environment verification (Conda, CLI, auth)
- File writing to `generated_agents/`
- Tool import (one per file)
- Agent import
- Dynamic chat URL generation
- Comprehensive error handling

**Files**:
- `deploy_agent.py`: Main deployment pipeline
- `orchestrate_env.py`: Environment verification
- `environment.yml`: Conda environment spec
- `.env`: Configuration (service URL, API key)

### ❌ FastAPI Backend (KAN-12) - TODO

**Purpose**: HTTP API layer connecting Bob Runner + Deployment

**Endpoints**:
```python
POST /generate-agent
  Body: { "prompt": "Create an agent that..." }
  Returns: { "task_id": "..." }
  
GET /status/{task_id}
  Returns: { "status": "generating|deploying|complete", ... }
  
GET /stream/{task_id}
  Server-Sent Events stream of progress updates
```

**Implementation**:
```python
from bob_runner import generate_agent
from deploy_agent import deploy_agent

@app.post("/generate-agent")
async def generate_agent_endpoint(request: GenerateRequest):
    # 1. Call bob_runner.generate_agent()
    generation_result = generate_agent(request.prompt)
    
    # 2. Call deploy_agent.deploy_agent()
    deployment_result = deploy_agent(generation_result)
    
    # 3. Return result
    return deployment_result
```

### ❌ Frontend (KAN-15) - TODO

**Purpose**: User interface for agent generation

**Components**:
- Chat input UI
- Real-time progress display
- Deployment result display
- Chat URL link

**Tech Stack**:
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- Server-Sent Events for progress

## 🧪 Testing Strategy

### Unit Tests
- ✅ `test_runner.py`: Bob Runner validation
- ✅ `test_deploy.py`: Deployment with mock data

### Integration Tests
- ✅ `test_e2e_integration.py`: Full pipeline (Bob → Deploy)

### Manual Testing
```bash
# 1. Test Bob Runner only
cd backend
python -c "from bob_runner import generate_agent; print(generate_agent('test agent'))"

# 2. Test Deployment only (with mock data)
cd backend
python test_deploy.py

# 3. Test Full Pipeline
cd backend
python test_e2e_integration.py
```

## 🔐 Security

### Credentials Management
- ✅ `.env` file for sensitive data
- ✅ `.env` in `.gitignore`
- ✅ `.env.example` template (no secrets)
- ✅ README warnings about security

### Environment Variables
```bash
ORCHESTRATE_SERVICE_URL=https://api.ca-tor.watson-orchestrate.cloud.ibm.com/instances/...
ORCHESTRATE_API_KEY=your_api_key_here
ORCHESTRATE_ENV_NAME=wx0-AWS
WXO_AGENT_DEPLOYMENT_TIMEOUT=300
```

## 🚀 Deployment Workflow

### Development
```bash
# 1. Setup
conda env create -f backend/environment.yml
conda activate watsonx
cp .env.example .env  # Edit with your credentials

# 2. Configure Orchestrate
orchestrate env activate wx0-AWS

# 3. Test
cd backend
python test_e2e_integration.py
```

### Production (Hackathon Demo)
```bash
# 1. Start FastAPI backend (KAN-12 - TODO)
uvicorn api.main:app --reload

# 2. Start Next.js frontend (KAN-15 - TODO)
cd frontend
npm run dev

# 3. Open browser
http://localhost:3000
```

## 📊 Success Metrics

### Hackathon Demo Goals
1. ✅ User types one sentence
2. ✅ Bob generates agent in ~30 seconds
3. ✅ Deployment completes in ~60 seconds
4. ✅ User gets working chat URL
5. ✅ Total time: ~90 seconds

### Technical Metrics
- ✅ Bob generation success rate: >90%
- ✅ Deployment success rate: >95%
- ✅ End-to-end success rate: >85%
- ✅ Average time: <120 seconds

## 🎯 Next Steps

### Immediate (For Hackathon)
1. **KAN-12**: Build FastAPI backend
   - Connect Bob Runner + Deployment
   - Add SSE for progress streaming
   - Error handling and retries

2. **KAN-15**: Build Next.js frontend
   - Chat input UI
   - Progress display
   - Result rendering

3. **Integration**: Connect all pieces
   - Frontend → Backend → Bob → Deploy
   - End-to-end testing
   - Demo preparation

### Future Enhancements
- Agent versioning
- Deployment history
- Agent templates
- Multi-region support
- Production deployment (draft → live)
- Agent monitoring and analytics

## 📚 References

- **ADK Documentation**: https://developer.watson-orchestrate.ibm.com
- **Bob Shell**: IBM internal tool
- **Task Tracking**: KAN-8 (Epic), KAN-11 (Bob), KAN-13 (Deploy)
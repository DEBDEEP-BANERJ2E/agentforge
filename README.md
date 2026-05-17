# AgentForge 🚀

**"Vercel for AI Agents"** - Type one sentence, get a deployed watsonx Orchestrate agent in 90 seconds.

[![Status](https://img.shields.io/badge/status-demo--ready-brightgreen)]()
[![Backend](https://img.shields.io/badge/backend-100%25-success)]()
[![Frontend](https://img.shields.io/badge/frontend-95%25-success)]()
[![Docs](https://img.shields.io/badge/docs-complete-blue)]()

---

## 🎯 What is AgentForge?

AgentForge transforms **natural language** into **production-ready AI agents** deployed on IBM watsonx Orchestrate.

**Example:**
```
User types: "Create an agent that determines if a release is safe to deploy"
                              ↓
AgentForge generates: agent.yaml + Python tools + requirements.txt
                              ↓
Deploys to: watsonx Orchestrate
                              ↓
Returns: Live chat URL (ready in ~90 seconds)
```

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ Start Backend (Terminal 1)
```bash
conda activate watsonx
orchestrate env activate wx0-AWS
./start_api.sh
```
✅ Verify: http://localhost:8000/health

### 2️⃣ Start Frontend (Terminal 2)
```bash
cd frontend
npm install  # First time only
npm run dev
```
✅ Verify: http://localhost:3000

### 3️⃣ Generate Your First Agent
1. Open http://localhost:3000
2. Type: **"Create an agent that fetches top 5 Hacker News stories"**
3. Click **"Generate Agent"**
4. Watch real-time progress
5. Click **"Open in Orchestrate"** when complete

**🎉 You just deployed an AI agent!**

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Next.js UI     │  User types prompt
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP POST
         ↓
┌─────────────────┐
│  FastAPI        │  Orchestrates generation + deployment
│  (Port 8000)    │
└────────┬────────┘
         │ calls
         ↓
┌─────────────────┐
│  Bob Runner     │  Generates agent.yaml + tools
│  (IBM Bob)      │
└────────┬────────┘
         │ returns AgentGenerationResult
         ↓
┌─────────────────┐
│  ADK Deployer   │  Deploys to Orchestrate
│  (orchestrate)  │
└────────┬────────┘
         │ deploys to
         ↓
┌─────────────────┐
│  watsonx        │  Live agent ready
│  Orchestrate    │
└─────────────────┘
```

---

## 📁 Project Structure

```
agentforge/
├── backend/                    # ✅ Python backend (100%)
│   ├── bob_runner.py          # Bob Shell wrapper
│   ├── deploy_agent.py        # ADK deployment engine
│   ├── orchestrate_env.py     # Environment verification
│   ├── models.py              # Data contracts
│   ├── parsers.py             # Output parsing
│   ├── validators.py          # Schema validation
│   └── environment.yml        # Conda environment
│
├── api/                        # ✅ FastAPI backend (100%)
│   ├── main.py                # FastAPI app
│   ├── routes.py              # API endpoints + SSE
│   └── test_api.py            # API tests
│
├── frontend/                   # ✅ Next.js frontend (95%)
│   ├── app/
│   │   ├── page.tsx           # Main UI (chat + progress)
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Tailwind styles
│   ├── package.json
│   └── next.config.mjs        # API proxy
│
├── .env                        # ✅ Configuration
├── start_api.sh               # Backend startup script
│
└── Documentation/              # ✅ Complete docs (100%)
    ├── COMPLETE_SETUP_GUIDE.md      # 👈 START HERE
    ├── ARCHITECTURE.md
    ├── API_DOCUMENTATION.md
    ├── DEPLOYMENT_SETUP.md
    └── HACKATHON_FINAL_STATUS.md
```

---

## 🎬 Demo Script (90 Seconds)

### Preparation
```bash
# Terminal 1: Backend
./start_api.sh

# Terminal 2: Frontend
cd frontend && npm run dev

# Browser: http://localhost:3000
```

### Live Demo
1. **[0:00-0:15]** Introduction
   - "AgentForge: From idea to deployed agent in 90 seconds"

2. **[0:15-0:45]** Live Generation
   - Type: "Create an agent that determines if a release is safe to deploy"
   - Show real-time progress: Understanding → Generating → Validating → Deploying

3. **[0:45-1:15]** Show Result
   - Agent deployed successfully
   - Open in watsonx Orchestrate
   - Demonstrate agent responding

4. **[1:15-1:30]** Closing
   - "From natural language to production in under 2 minutes"

---

## 🚀 Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🤖 AI Generation | ✅ Ready | IBM Bob Shell generates ADK-compliant code |
| ✅ Validation | ✅ Ready | Schema + syntax validation before deploy |
| 🚀 Deployment | ✅ Ready | Automatic ADK deployment to Orchestrate |
| 📊 Real-Time Progress | ✅ Ready | SSE streaming for live updates |
| 💬 Modern UI | ✅ Ready | Next.js + Tailwind + TypeScript |
| 📚 Documentation | ✅ Complete | 5 comprehensive guides |

---

## 📚 Documentation

| Document | Purpose | Status |
|----------|---------|--------|
| **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)** | 👈 **START HERE** - Setup + demo guide | ✅ Complete |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture + design decisions | ✅ Complete |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | API reference + examples | ✅ Complete |
| [DEPLOYMENT_SETUP.md](DEPLOYMENT_SETUP.md) | Deployment configuration | ✅ Complete |
| [HACKATHON_FINAL_STATUS.md](HACKATHON_FINAL_STATUS.md) | Status + 5 killer demo ideas | ✅ Complete |
| [frontend/README.md](frontend/README.md) | Frontend-specific docs | ✅ Complete |

---

## 🎯 Example Prompts

Try these in the UI:

1. **🚨 Incident Management**
   ```
   Create an agent that creates incident war rooms when production fails
   ```

2. **✅ Release Safety**
   ```
   Create an agent that determines if a release is safe to deploy
   ```

3. **📰 News Digest**
   ```
   Create an agent that fetches top 5 Hacker News stories
   ```

4. **🔧 Code Modernization**
   ```
   Create an agent that upgrades legacy code with tests
   ```

5. **🔍 Vendor Risk**
   ```
   Create an agent that evaluates vendor security and compliance
   ```

---

## 🧪 Testing

### Test Backend
```bash
cd backend
python test_e2e_integration.py
```

### Test API
```bash
cd api
python test_api.py
```

### Test Frontend
```bash
cd frontend
npm run dev
# Open http://localhost:3000 and generate an agent
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Conda environment
conda activate watsonx
python --version  # Should be 3.12.x

# Check Orchestrate
orchestrate env activate wx0-AWS
orchestrate agents list
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### API connection failed
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend proxy in next.config.mjs
```

**See [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) for detailed troubleshooting.**

---

## 📊 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend (Bob Runner) | ⚠️ 85% | Needs KAN-11 compliance fixes |
| Backend (ADK Deployment) | ✅ 100% | Fully functional |
| FastAPI Backend | ✅ 100% | SSE + endpoints working |
| Next.js Frontend | ✅ 95% | Needs `npm install` + testing |
| Documentation | ✅ 100% | 5 comprehensive guides |
| **Overall** | ✅ **~90%** | **Demo-ready** |

---

## 🎓 Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **AI**: IBM Bob Shell (custom Agent Architect mode)
- **Deployment**: IBM watsonx Orchestrate ADK
- **Environment**: Conda, Node.js

---

## 🏆 Built For

**IBM Bob Hackathon 2026**

**Team:**
- Debdeep (ADK Deployment)
- Varun (ADK Deployment)
- Eman (Bob Wrapper)
- Denis (Bob Wrapper)
- Jawad (Frontend)
- Aditya (Demo & Storytelling)

---

## 📝 License

MIT

---

## 🚀 Next Steps

1. **Install frontend dependencies**: `cd frontend && npm install`
2. **Start both servers**: Backend + Frontend
3. **Generate your first agent**: http://localhost:3000
4. **Read the docs**: [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)

**Happy hacking! 🎉**

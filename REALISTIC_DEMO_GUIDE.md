# 🎯 Realistic Working Demos - AgentForge Catalog Tools

## ✅ Tools That Work RIGHT NOW (No Auth Needed)

Based on your deployed tools, these use **public APIs** and work immediately:

### 🌐 Web & News
- **`hacker_news`** - Fetches top 5 Hacker News stories
- **`hacker_news_fetcher`** - Fetches top 5 Hacker News stories

### 💰 Crypto
- **`coingecko_api`** - Fetches Bitcoin, Ethereum, Solana prices from CoinGecko

### 🌤️ Weather & Environment
- **`open_meteo`** - Fetches current weather for a city
- **`open_meteo_weather`** - Get current weather for a given city
- **`air_quality`** - Fetches current air quality index for a city

### 🌍 Geography
- **`rest_countries_api`** - Looks up country info (capital, population, region, currencies)

### 📚 Books (Likely Works)
- **`search_by_title`** - Search for books by title (Open Library API is public)
- **`fetch_by_id`** - Fetch full details by Open Library book ID

### 🔧 Utilities
- **`ping`** - Returns a simple ping response

---

## ❌ Tools That Need Authentication

### 🐙 GitHub Tools (Need Personal Access Token)
- `github_trending`
- `github_commits`
- `github_pull_requests`
- `github_ci_checks`

**Why they fail:** GitHub API requires authentication for most endpoints.

**How to fix (optional):**
1. Get token: https://github.com/settings/tokens
2. Modify tool code to include: `headers={"Authorization": f"token {GITHUB_TOKEN}"}`

**For demo:** Skip these or mention as "future state when GitHub connection is configured"

---

## 🔥 3 Killer Demos That Work NOW

### Demo 1: Multi-Source News & Crypto Dashboard
**Prompt:**
```
Create an agent that fetches top Hacker News stories and current crypto prices
```

**What Happens:**
1. AgentForge discovers: `hacker_news`, `coingecko_api`
2. LLM generates YAML referencing both
3. **Zero Python code written**
4. Agent deployed in ~30 seconds

**Generated YAML:**
```yaml
spec_version: v1
kind: native
name: news_crypto_dashboard
description: Fetches Hacker News stories and crypto prices
llm: watsonx/meta-llama/llama-3-2-90b-vision-instruct
style: default
instructions: |
  Fetch the top Hacker News stories and current prices for Bitcoin, Ethereum, and Solana.
  Present the information in a clear, organized format.
tools: [hacker_news, coingecko_api]
```

**Demo in Orchestrate:**
```
User: "Show me tech news and crypto prices"

Agent: 
[Calls hacker_news tool]
[Calls coingecko_api tool]

Top Hacker News Stories:
1. New AI breakthrough...
2. Startup raises $50M...
...

Crypto Prices:
- Bitcoin: $45,234
- Ethereum: $2,891
- Solana: $98.45
```

**Why It's Killer:**
- ✅ Works immediately (public APIs)
- ✅ Zero code written
- ✅ Combines 2 data sources
- ✅ Practical use case
- ✅ Judges can test it live

---

### Demo 2: Weather Intelligence Agent
**Prompt:**
```
Create an agent that provides weather and air quality information for any city
```

**What Happens:**
1. AgentForge discovers: `open_meteo_weather`, `air_quality`
2. LLM generates YAML referencing both
3. **Zero Python code written**
4. Agent provides comprehensive environmental data

**Generated YAML:**
```yaml
spec_version: v1
kind: native
name: weather_intelligence
description: Provides weather and air quality data for cities
llm: watsonx/meta-llama/llama-3-2-90b-vision-instruct
style: default
instructions: |
  Provide comprehensive weather and air quality information for any requested city.
  Include temperature, conditions, and air quality index with health recommendations.
tools: [open_meteo_weather, air_quality]
```

**Demo in Orchestrate:**
```
User: "What's the weather and air quality in London?"

Agent:
[Calls open_meteo_weather for London]
[Calls air_quality for London]

Weather in London:
- Temperature: 15°C
- Conditions: Partly cloudy
- Humidity: 72%

Air Quality:
- AQI: 42 (Good)
- Recommendation: Air quality is satisfactory
```

**Why It's Killer:**
- ✅ Works immediately
- ✅ Intelligent tool composition
- ✅ Practical for travel/health
- ✅ Shows environmental awareness

---

### Demo 3: Travel Planning Assistant
**Prompt:**
```
Create an agent that helps plan travel by providing weather and country information
```

**What Happens:**
1. AgentForge discovers: `open_meteo_weather`, `rest_countries_api`
2. LLM generates YAML combining both
3. **Zero Python code written**
4. Agent provides comprehensive travel intel

**Generated YAML:**
```yaml
spec_version: v1
kind: native
name: travel_planner
description: Provides weather and country information for travel planning
llm: watsonx/meta-llama/llama-3-2-90b-vision-instruct
style: default
instructions: |
  Help users plan travel by providing current weather conditions and essential
  country information including capital, population, region, and currencies.
tools: [open_meteo_weather, rest_countries_api]
```

**Demo in Orchestrate:**
```
User: "I'm planning a trip to Japan, what should I know?"

Agent:
[Calls rest_countries_api for Japan]
[Calls open_meteo_weather for Tokyo]

Japan Travel Information:

Country Details:
- Capital: Tokyo
- Population: 125.8 million
- Region: Asia
- Currency: Japanese Yen (JPY)

Current Weather in Tokyo:
- Temperature: 22°C
- Conditions: Clear
- Perfect for sightseeing!
```

**Why It's Killer:**
- ✅ Works immediately
- ✅ Combines geographic + weather data
- ✅ Practical travel use case
- ✅ Shows intelligent data fusion

---

## 🎬 5-Minute Hackathon Demo Script

### Setup (Before Demo)
1. Have AgentForge running: http://localhost:3000
2. Have Orchestrate open in another tab
3. Test one agent beforehand to ensure it works

### Opening (30 seconds)
> "AgentForge automatically discovers existing tools and intelligently reuses them. Let me show you three real examples that work right now."

### Demo 1: News & Crypto (90 seconds)
**Type:** "Create an agent that fetches top Hacker News stories and current crypto prices"

**Show:**
1. Real-time progress: "Discovering tools..."
2. Generated YAML: `tools: [hacker_news, coingecko_api]`
3. No Python files generated
4. Agent deployed

**Switch to Orchestrate:**
```
"Show me tech news and crypto prices"
```

**Watch it work live!**

**Say:** "Zero code written. It found two existing tools and composed them."

### Demo 2: Weather Intelligence (90 seconds)
**Type:** "Create an agent that provides weather and air quality for any city"

**Show:**
1. Discovers: `open_meteo_weather`, `air_quality`
2. YAML: `tools: [open_meteo_weather, air_quality]`
3. No Python code

**Switch to Orchestrate:**
```
"What's the weather and air quality in San Francisco?"
```

**Watch it work!**

**Say:** "Intelligent composition. It knew these two tools together provide complete environmental data."

### Demo 3: Travel Planner (90 seconds)
**Type:** "Create an agent that helps plan travel with weather and country info"

**Show:**
1. Discovers: `open_meteo_weather`, `rest_countries_api`
2. YAML combines both
3. No Python code

**Switch to Orchestrate:**
```
"I'm planning a trip to Brazil, what should I know?"
```

**Watch it work!**

**Say:** "This is data fusion. Weather plus geography. Zero code. 60 seconds."

### Closing (30 seconds)
> "These are just 9 of the 14 tools we have deployed. When you connect GitHub, Slack, Jira in Orchestrate, you get 1,119+ tools. AgentForge becomes a universal agent factory for any enterprise workflow."

**End with:** "Questions?"

---

## 🧪 Pre-Demo Testing Checklist

### 1. Test Tool Discovery
```bash
cd backend
python catalog_tools.py
```

**Verify output shows 14 tools.**

### 2. Test One Agent End-to-End
```bash
# Start backend
./start_api.sh

# Start frontend (new terminal)
cd frontend && npm run dev
```

**Generate:** "Create an agent that fetches Hacker News stories"

**Verify:**
- Agent generated successfully
- YAML includes `tools: [hacker_news]`
- No Python files
- Agent appears in Orchestrate

### 3. Test Agent in Orchestrate
Open the generated agent and chat:
```
fetch me the top hacker news stories
```

**Verify:** Tool executes and returns stories.

### 4. Have Backup
If live demo fails, have screenshots/video of it working.

---

## 💡 Handling Questions

### Q: "What if I need a tool that doesn't exist?"
**A:** "AgentForge generates Python code for new capabilities. It intelligently mixes existing and new tools in the same agent."

### Q: "How does it know which tools to use?"
**A:** "It uses keyword-based relevance matching. When you type 'weather', it finds weather-related tools. For production, we'd use embeddings for semantic search."

### Q: "What about authentication?"
**A:** "Public API tools work immediately. For authenticated services like GitHub, you configure connections in Orchestrate UI once, then all agents can use those tools."

### Q: "How many tools are available?"
**A:** "We have 14 custom tools deployed. When you connect services in Orchestrate, you get 1,119+ enterprise tools. The system scales automatically."

---

## 🎯 Key Talking Points

1. **"Zero Code"** - Emphasize no Python written for these demos
2. **"Intelligent Composition"** - LLM understands which tools to combine
3. **"Works Now"** - These aren't mockups, they're live and working
4. **"Scales"** - Same pattern works with 1,119+ tools
5. **"Enterprise Ready"** - Uses battle-tested catalog tools

---

## 📊 Success Metrics

### What Makes a Good Demo
- ✅ Works reliably (public APIs)
- ✅ Visually impressive (real-time generation)
- ✅ Practical use case (not toy examples)
- ✅ Shows intelligence (tool composition)
- ✅ Fast (30-60 seconds)

### What to Avoid
- ❌ Tools that need auth (GitHub without token)
- ❌ Complex multi-step workflows (too slow)
- ❌ Toy examples (hello world)
- ❌ Anything that might fail live

---

## 🚀 Post-Demo: Scaling Story

**After showing working demos, explain the vision:**

> "What you just saw works with 14 tools. But the real power comes when you scale:
> 
> - Connect GitHub → 50+ tools (create issues, PRs, comments)
> - Connect Slack → 30+ tools (post messages, create channels)
> - Connect Jira → 40+ tools (create tickets, update status)
> - Connect Salesforce → 100+ tools (CRM operations)
> 
> AgentForge automatically discovers all of them. The same prompt that worked with 14 tools works with 1,119 tools. That's the vision: a universal agent factory for enterprise workflows."

---

## 📝 Summary

**Focus on what works:**
- ✅ Hacker News + Crypto = News Dashboard
- ✅ Weather + Air Quality = Environmental Intelligence
- ✅ Weather + Country Info = Travel Assistant

**Mention as future:**
- GitHub tools (when connection configured)
- Slack tools (when connection configured)
- 1,119+ catalog tools (when services connected)

**Key message:**
> "AgentForge doesn't just generate code—it intelligently reuses what exists. Zero code, 60 seconds, production-ready agents."

---

**Built for IBM Bob Hackathon 2026** 🚀
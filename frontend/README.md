# AgentForge Frontend

Modern Next.js frontend for AgentForge - the AI Agent Generator.

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

### 3. Make Sure Backend is Running

The frontend connects to the FastAPI backend at http://localhost:8000

```bash
# In the project root
./start_api.sh
```

## Features

- **Modern UI**: Clean, minimalist design with Tailwind CSS
- **Real-time Updates**: Server-Sent Events for live progress
- **Responsive**: Works on desktop and mobile
- **Dark Mode**: Automatic dark mode support
- **Error Handling**: Clear error messages and recovery

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page with all components
│   └── globals.css         # Global styles
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── tailwind.config.ts      # Tailwind config
├── postcss.config.mjs      # PostCSS config
└── next.config.mjs         # Next.js config
```

## Components

All components are in `app/page.tsx`:

- **Header**: App branding and navigation
- **Chat Input**: Text area for agent description
- **Progress Display**: Real-time build status with stages
- **Result Card**: Deployed agent info with chat URL
- **Error Display**: Error messages and troubleshooting

## API Integration

The frontend connects to the FastAPI backend via:

- **POST /api/generate-agent**: Start agent generation
- **GET /api/stream/{task_id}**: SSE stream for progress

See `next.config.mjs` for API proxy configuration.

## Environment Variables

Create `.env.local` if you need to customize:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Build for Production

```bash
npm run build
npm start
```

## Technologies

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first CSS
- **Lucide React**: Icon library
- **EventSource**: Server-Sent Events client

## Troubleshooting

### Port 3000 already in use

```bash
# Kill the process
lsof -ti:3000 | xargs kill -9

# Or use a different port
PORT=3001 npm run dev
```

### Backend not connecting

1. Make sure FastAPI is running: http://localhost:8000/health
2. Check CORS configuration in `api/main.py`
3. Verify proxy in `next.config.mjs`

### TypeScript errors

```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
```

## Demo

The frontend is designed for live demos with:

- Fast input and submission
- Visual progress tracking
- Clear success/error states
- One-click access to deployed agents

Perfect for the 90-second hackathon demo!
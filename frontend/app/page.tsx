'use client';

import { useState, useEffect, useRef } from 'react';
import { Sparkles, Loader2, CheckCircle2, XCircle, ExternalLink, ArrowRight, Zap, Globe, Shield, Clock } from 'lucide-react';
import EmbedGenerator from './components/EmbedGenerator';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TaskStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  stage: string;
  progress: number;
  message: string;
  agent_name?: string;
  chat_url?: string;
  errors: string[];
}

const EXAMPLES = [
  { label: 'Weather', prompt: 'Create an agent that fetches the current weather for a given city using the Open-Meteo API' },
  { label: 'Air Quality', prompt: 'Create an agent that fetches the current air quality index for a given city using the Open-Meteo air quality API' },
  { label: 'Crypto Prices', prompt: 'Create an agent that fetches the current prices of Bitcoin, Ethereum, and Solana in USD from the CoinGecko public API' },
  { label: 'Wikipedia', prompt: 'Create an agent that searches Wikipedia for a topic the user provides and returns a plain-English summary' },
  { label: 'Currency Converter', prompt: 'Create an agent that converts a currency amount from one currency to another using the Frankfurter API' },
  { label: 'Country Facts', prompt: 'Create an agent that looks up a country by name and returns its capital, population, region, and currencies using the REST Countries API' },
  { label: 'Dev Jokes', prompt: 'Create an agent that fetches a random programming joke from the JokeAPI' },
];

const STAGES = [
  { key: 'initializing', label: 'Parsing' },
  { key: 'generating',   label: 'Generating' },
  { key: 'validating',   label: 'Validating' },
  { key: 'deploying',    label: 'Deploying' },
  { key: 'deployed',     label: 'Live' },
];

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    return () => { eventSourceRef.current?.close(); };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError(null);
    setTaskStatus(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim() }),
      });

      if (!response.ok) throw new Error('Failed to start agent generation');

      const { task_id } = await response.json();
      const eventSource = new EventSource(`${API_BASE_URL}/api/stream/${task_id}`);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        const status: TaskStatus = JSON.parse(event.data);
        setTaskStatus(status);
        if (status.status === 'completed' || status.status === 'failed') {
          eventSource.close();
          setIsGenerating(false);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setError('Connection lost. Please try again.');
        setIsGenerating(false);
      };
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsGenerating(false);
    }
  };

  const currentStageIndex = STAGES.findIndex(s => s.key === taskStatus?.stage);

  const getStageState = (index: number) => {
    if (!taskStatus) return 'idle';
    if (taskStatus.status === 'failed') return index <= currentStageIndex ? 'failed' : 'idle';
    if (index < currentStageIndex) return 'done';
    if (index === currentStageIndex) return 'active';
    return 'idle';
  };

  return (
    <div className="min-h-screen bg-dot-grid" style={{ background: '#020208' }}>

      {/* Background glows */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="animate-glow-pulse absolute top-[-200px] left-[-200px] w-[600px] h-[600px] rounded-full"
          style={{ background: 'radial-gradient(circle, #6366f118 0%, transparent 70%)' }} />
        <div className="animate-glow-pulse absolute bottom-[-200px] right-[-200px] w-[700px] h-[700px] rounded-full"
          style={{ background: 'radial-gradient(circle, #8b5cf618 0%, transparent 70%)', animationDelay: '2s' }} />
        <div className="absolute inset-0 bg-dot-grid opacity-30" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)', background: 'rgba(2,2,8,0.8)', backdropFilter: 'blur(20px)' }}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="text-white font-semibold tracking-tight text-lg">AgentForge</span>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden sm:flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-full"
              style={{ background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', color: '#a5b4fc' }}>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Powered by IBM watsonx
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="relative z-10 max-w-4xl mx-auto px-6 pt-20 pb-32">

        {/* Hero */}
        <div className="text-center mb-14 animate-fade-up">
          <div className="inline-flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-full mb-6"
            style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', color: '#818cf8' }}>
            <Zap className="w-3 h-3" />
            Deploy to IBM Orchestrate in ~90 seconds
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-white mb-5 leading-tight">
            Build AI agents{' '}
            <span className="shimmer-text">from plain English</span>
          </h1>

          <p className="text-lg max-w-xl mx-auto" style={{ color: '#94a3b8' }}>
            Describe what you want. AgentForge writes the code, validates it, and deploys a live watsonx Orchestrate agent — no YAML, no SDK, no setup.
          </p>
        </div>

        {/* Input card */}
        <div className="glass-strong rounded-2xl p-6 mb-4 animate-fade-up" style={{ animationDelay: '0.1s' }}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Create an agent that fetches the current weather for a given city using the Open-Meteo API"
              disabled={isGenerating}
              rows={3}
              className="textarea-glow w-full rounded-xl px-4 py-3.5 text-sm resize-none transition-all duration-200"
              style={{
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: '#e2e8f0',
                outline: 'none',
              }}
            />

            <button
              type="submit"
              disabled={isGenerating || !prompt.trim()}
              className="btn-primary w-full flex items-center justify-center gap-2.5 py-3.5 px-6 rounded-xl text-sm font-semibold text-white"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating Agent...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Agent
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Example chips */}
        {!isGenerating && !taskStatus && (
          <div className="animate-fade-up mb-12" style={{ animationDelay: '0.2s' }}>
            <p className="text-xs mb-3 text-center" style={{ color: '#475569' }}>Try an example</p>
            <div className="flex flex-wrap justify-center gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex.label}
                  onClick={() => setPrompt(ex.prompt)}
                  className="chip px-3.5 py-1.5 rounded-full text-xs font-medium transition-all"
                  style={{ background: 'rgba(255,255,255,0.03)', color: '#64748b' }}
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Progress */}
        {taskStatus && (isGenerating || taskStatus.status === 'completed' || taskStatus.status === 'failed') && (
          <div className="glass rounded-2xl p-6 mb-4 animate-fade-up">

            {/* Stage pipeline */}
            <div className="flex items-center justify-between mb-6">
              {STAGES.map((stage, i) => {
                const state = getStageState(i);
                return (
                  <div key={stage.key} className="flex items-center flex-1">
                    <div className="flex flex-col items-center gap-1.5">
                      <div className="w-7 h-7 rounded-full flex items-center justify-center transition-all duration-300"
                        style={{
                          background: state === 'done' ? '#10b981' :
                                      state === 'active' ? '#6366f1' :
                                      state === 'failed' ? '#ef4444' : 'rgba(255,255,255,0.06)',
                          boxShadow: state === 'active' ? '0 0 16px #6366f180' :
                                     state === 'done' ? '0 0 12px #10b98150' : 'none',
                        }}>
                        {state === 'done' && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                        {state === 'active' && <Loader2 className="w-3.5 h-3.5 text-white animate-spin" />}
                        {state === 'failed' && <XCircle className="w-3.5 h-3.5 text-white" />}
                        {state === 'idle' && <div className="w-1.5 h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.2)' }} />}
                      </div>
                      <span className="text-xs font-medium" style={{
                        color: state === 'active' ? '#a5b4fc' :
                               state === 'done' ? '#34d399' :
                               state === 'failed' ? '#f87171' : '#334155'
                      }}>
                        {stage.label}
                      </span>
                    </div>
                    {i < STAGES.length - 1 && (
                      <div className="flex-1 h-px mx-2 mb-5 transition-all duration-500"
                        style={{ background: state === 'done' ? '#10b98150' : 'rgba(255,255,255,0.06)' }} />
                    )}
                  </div>
                );
              })}
            </div>

            {/* Progress bar */}
            <div className="w-full rounded-full overflow-hidden mb-3" style={{ height: '3px', background: 'rgba(255,255,255,0.06)' }}>
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${taskStatus.progress}%`,
                  background: taskStatus.status === 'failed'
                    ? '#ef4444'
                    : 'linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4)',
                  boxShadow: taskStatus.status !== 'failed' ? '0 0 12px #6366f180' : 'none',
                }}
              />
            </div>

            <p className="text-xs" style={{ color: '#475569' }}>{taskStatus.message}</p>
          </div>
        )}

        {/* Success card */}
        {taskStatus?.status === 'completed' && taskStatus.chat_url && (
          <>
            <div className="rounded-2xl p-6 animate-fade-up" style={{
              background: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,182,212,0.06))',
              border: '1px solid rgba(16,185,129,0.2)',
            }}>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)' }}>
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-white mb-0.5">Agent deployed successfully</p>
                  <p className="text-xs mb-4" style={{ color: '#64748b' }}>
                    <span className="font-mono" style={{ color: '#94a3b8' }}>{taskStatus.agent_name}</span> is live in IBM watsonx Orchestrate
                  </p>
                  <a
                    href={taskStatus.chat_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 hover:opacity-90"
                    style={{ background: 'rgba(16,185,129,0.2)', border: '1px solid rgba(16,185,129,0.35)', color: '#34d399' }}
                  >
                    Open in IBM Orchestrate
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            </div>

            {/* Embed Generator */}
            <EmbedGenerator
              agentId={taskStatus.agent_name || 'agent'}
              agentName={taskStatus.agent_name || 'AI Agent'}
              orchestrationID="6c32a116d8ed4b058c1dfd87f61222e6_4e732bf0-848b-4b3d-be31-f80c223c0950"
              hostURL="https://ca-tor.watson-orchestrate.cloud.ibm.com"
              crn="crn:v1:bluemix:public:watsonx-orchestrate:ca-tor:a/6c32a116d8ed4b058c1dfd87f61222e6:4e732bf0-848b-4b3d-be31-f80c223c0950::"
            />
          </>
        )}

        {/* Error card */}
        {(error || (taskStatus?.status === 'failed' && taskStatus.errors.length > 0)) && (
          <div className="rounded-2xl p-6 animate-fade-up" style={{
            background: 'rgba(239,68,68,0.06)',
            border: '1px solid rgba(239,68,68,0.2)',
          }}>
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)' }}>
                <XCircle className="w-5 h-5 text-red-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white mb-1">Generation failed</p>
                <div className="text-xs space-y-1" style={{ color: '#f87171' }}>
                  {error && <p>{error}</p>}
                  {taskStatus?.errors.map((err, i) => <p key={i}>{err}</p>)}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats row */}
        {!taskStatus && !isGenerating && (
          <div className="grid grid-cols-3 gap-4 mt-16 animate-fade-up" style={{ animationDelay: '0.3s' }}>
            {[
              { icon: Clock, label: '~90 seconds', sub: 'From prompt to live agent' },
              { icon: Globe, label: 'Zero code', sub: 'No YAML, SDK, or CLI needed' },
              { icon: Shield, label: 'IBM Cloud', sub: 'Deployed to watsonx Orchestrate' },
            ].map(({ icon: Icon, label, sub }) => (
              <div key={label} className="glass rounded-xl p-4 text-center">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center mx-auto mb-3"
                  style={{ background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.2)' }}>
                  <Icon className="w-4 h-4" style={{ color: '#818cf8' }} />
                </div>
                <p className="text-sm font-semibold text-white mb-0.5">{label}</p>
                <p className="text-xs" style={{ color: '#475569' }}>{sub}</p>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t py-6" style={{ borderColor: 'rgba(255,255,255,0.05)' }}>
        <p className="text-center text-xs" style={{ color: '#1e293b' }}>
          Built for IBM watsonx Hackathon 2026 · AgentForge
        </p>
      </footer>
    </div>
  );
}

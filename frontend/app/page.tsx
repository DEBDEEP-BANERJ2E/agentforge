'use client';

import { useState, useEffect, useRef } from 'react';
import { Sparkles, Loader2, CheckCircle2, XCircle, ExternalLink, Zap } from 'lucide-react';

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

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setError(null);
    setTaskStatus(null);

    try {
      // Start generation
      const response = await fetch(`${API_BASE_URL}/api/generate-agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: prompt.trim() }),
      });

      if (!response.ok) {
        throw new Error('Failed to start agent generation');
      }

      const data = await response.json();
      const taskId = data.task_id;

      // Connect to SSE stream
      const eventSource = new EventSource(`${API_BASE_URL}/api/stream/${taskId}`);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        const status: TaskStatus = JSON.parse(event.data);
        setTaskStatus(status);

        // Close connection when complete or failed
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

  const getStageIcon = (stage: string) => {
    if (taskStatus?.status === 'completed') return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    if (taskStatus?.status === 'failed') return <XCircle className="w-5 h-5 text-red-500" />;
    return <Loader2 className="w-5 h-5 animate-spin text-blue-500" />;
  };

  const getStageColor = (stage: string) => {
    const stages = ['initializing', 'generating', 'validating', 'deploying', 'deployed'];
    const currentIndex = stages.indexOf(taskStatus?.stage || '');
    const stageIndex = stages.indexOf(stage);
    
    if (taskStatus?.status === 'failed') return 'bg-red-500';
    if (stageIndex < currentIndex) return 'bg-green-500';
    if (stageIndex === currentIndex) return 'bg-blue-500';
    return 'bg-gray-300';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AgentForge</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">AI Agent Generator</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
              <Zap className="w-4 h-4" />
              <span>Powered by watsonx</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Input */}
          <div className="lg:col-span-2 space-y-6">
            {/* Hero Section */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-8 border border-gray-200 dark:border-gray-700">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Create AI Agents in Seconds
              </h2>
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                Type one sentence. Get a deployed watsonx Orchestrate agent in ~90 seconds.
              </p>

              {/* Input Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Describe your agent
                  </label>
                  <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Example: Create an agent that summarizes Hacker News every morning and posts to Slack"
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                    rows={4}
                    disabled={isGenerating}
                  />
                </div>

                <button
                  type="submit"
                  disabled={isGenerating || !prompt.trim()}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Generating Agent...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      <span>Generate Agent</span>
                    </>
                  )}
                </button>
              </form>

              {/* Example Prompts */}
              {!isGenerating && !taskStatus && (
                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Try these examples:</p>
                  <div className="space-y-2">
                    {[
                      "Create an agent that creates incident war rooms when production fails",
                      "Create an agent that determines if a release is safe to deploy",
                      "Create an agent that fetches top 5 Hacker News stories",
                    ].map((example, i) => (
                      <button
                        key={i}
                        onClick={() => setPrompt(example)}
                        className="w-full text-left px-4 py-2 text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                      >
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Result Card */}
            {taskStatus?.status === 'completed' && taskStatus.chat_url && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl shadow-sm p-6 border border-green-200 dark:border-green-800">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <CheckCircle2 className="w-8 h-8 text-green-500" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      Agent Deployed Successfully! 🎉
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">
                      Your agent <span className="font-mono font-semibold">{taskStatus.agent_name}</span> is now live and ready to use.
                    </p>
                    <a
                      href={taskStatus.chat_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      <span>Open in Orchestrate</span>
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* Error Card */}
            {(error || (taskStatus?.status === 'failed' && taskStatus.errors.length > 0)) && (
              <div className="bg-red-50 dark:bg-red-900/20 rounded-xl shadow-sm p-6 border border-red-200 dark:border-red-800">
                <div className="flex items-start space-x-4">
                  <XCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-red-900 dark:text-red-200 mb-2">
                      Generation Failed
                    </h3>
                    <div className="text-red-700 dark:text-red-300 space-y-1">
                      {error && <p>{error}</p>}
                      {taskStatus?.errors.map((err, i) => (
                        <p key={i}>{err}</p>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Progress */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700 sticky top-8">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Build Status
              </h3>

              {!taskStatus ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">Waiting to start...</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Progress Bar */}
                  <div>
                    <div className="flex justify-between text-sm text-gray-600 dark:text-gray-300 mb-2">
                      <span>Progress</span>
                      <span className="font-semibold">{taskStatus.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-600 h-full transition-all duration-500 ease-out"
                        style={{ width: `${taskStatus.progress}%` }}
                      />
                    </div>
                  </div>

                  {/* Current Stage */}
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStageIcon(taskStatus.stage)}
                      <span className="font-semibold text-gray-900 dark:text-white capitalize">
                        {taskStatus.stage.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 ml-8">
                      {taskStatus.message}
                    </p>
                  </div>

                  {/* Stage Timeline */}
                  <div className="space-y-3">
                    {[
                      { key: 'initializing', label: 'Understanding' },
                      { key: 'generating', label: 'Generating' },
                      { key: 'validating', label: 'Validating' },
                      { key: 'deploying', label: 'Deploying' },
                      { key: 'deployed', label: 'Ready' },
                    ].map((stage) => (
                      <div key={stage.key} className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${getStageColor(stage.key)}`} />
                        <span className="text-sm text-gray-600 dark:text-gray-300">
                          {stage.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            Built for IBM Bob Hackathon 2026 • Powered by watsonx Orchestrate
          </p>
        </div>
      </footer>
    </div>
  );
}

// Made with Bob

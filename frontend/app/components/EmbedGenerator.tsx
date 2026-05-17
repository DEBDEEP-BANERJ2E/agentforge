'use client';

import { useState } from 'react';
import { Download, ExternalLink, Copy, Check } from 'lucide-react';

interface EmbedGeneratorProps {
  agentId: string;
  agentName: string;
  orchestrationID: string;
  hostURL: string;
  crn: string;
}

export default function EmbedGenerator({
  agentId,
  agentName,
  orchestrationID,
  hostURL,
  crn,
}: EmbedGeneratorProps) {
  const [copied, setCopied] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const generateHTML = () => {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${agentName} - AI Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1.5rem 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 1.75rem;
            color: #1a202c;
            font-weight: 700;
        }
        
        .header p {
            color: #718096;
            margin-top: 0.25rem;
            font-size: 0.95rem;
        }
        
        .container {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .chat-wrapper {
            width: 100%;
            max-width: 900px;
            height: 600px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        #root {
            width: 100%;
            height: 100%;
        }
        
        .footer {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            text-align: center;
            color: white;
            font-size: 0.875rem;
        }
        
        .footer a {
            color: white;
            text-decoration: underline;
            font-weight: 600;
        }
        
        @media (max-width: 768px) {
            .chat-wrapper {
                height: 500px;
                border-radius: 12px;
            }
            
            .header h1 {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>${agentName}</h1>
        <p>Powered by watsonx Orchestrate & AgentForge</p>
    </div>
    
    <div class="container">
        <div class="chat-wrapper">
            <div id="root"></div>
        </div>
    </div>
    
    <div class="footer">
        Built with <a href="https://github.com/bladedevoff/agentforge" target="_blank">AgentForge</a> 
        | IBM Bob Hackathon 2026
    </div>

    <script>
        window.wxOConfiguration = {
            orchestrationID: "${orchestrationID}",
            hostURL: "${hostURL}",
            rootElementID: "root",
            deploymentPlatform: "ibmcloud",
            crn: "${crn}",
            chatOptions: {
                agentId: "${agentId}", 
            }
        };
        
        setTimeout(function () {
            const script = document.createElement('script');
            script.src = \`\${window.wxOConfiguration.hostURL}/wxochat/wxoLoader.js?embed=true\`;
            script.addEventListener('load', function () {
                wxoLoader.init();
            });
            document.head.appendChild(script);
        }, 0);
    </script>
</body>
</html>`;
  };

  const handleDownload = () => {
    const html = generateHTML();
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${agentName.replace(/\s+/g, '-').toLowerCase()}-agent.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 3000);
  };

  const handleCopy = () => {
    const html = generateHTML();
    navigator.clipboard.writeText(html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePreview = () => {
    const html = generateHTML();
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  return (
    <div className="mt-6 p-6 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border-2 border-purple-200">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <ExternalLink className="w-5 h-5 text-purple-600" />
            Embeddable Webpage
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Create a standalone webpage for your agent
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <button
          onClick={handleDownload}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 font-medium shadow-lg hover:shadow-xl"
        >
          {downloadSuccess ? (
            <>
              <Check className="w-5 h-5" />
              Downloaded!
            </>
          ) : (
            <>
              <Download className="w-5 h-5" />
              Download HTML Page
            </>
          )}
        </button>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleCopy}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200 font-medium border-2 border-gray-200 hover:border-purple-300"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-green-600" />
                <span className="text-green-600">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy HTML
              </>
            )}
          </button>

          <button
            onClick={handlePreview}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200 font-medium border-2 border-gray-200 hover:border-purple-300"
          >
            <ExternalLink className="w-4 h-4" />
            Preview
          </button>
        </div>
      </div>

      <div className="mt-4 p-4 bg-white rounded-lg border border-purple-200">
        <h4 className="text-sm font-semibold text-gray-900 mb-2">
          📦 Deployment Options
        </h4>
        <ul className="text-sm text-gray-600 space-y-1.5">
          <li className="flex items-start gap-2">
            <span className="text-purple-600 font-bold">•</span>
            <span><strong>Vercel:</strong> Drag & drop HTML file to <a href="https://vercel.com" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline">vercel.com</a></span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-600 font-bold">•</span>
            <span><strong>Netlify:</strong> Drop file at <a href="https://app.netlify.com/drop" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline">netlify.com/drop</a></span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-600 font-bold">•</span>
            <span><strong>GitHub Pages:</strong> Push to repo and enable Pages</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-600 font-bold">•</span>
            <span><strong>Any Web Server:</strong> Upload HTML file anywhere</span>
          </li>
        </ul>
      </div>

      <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-xs text-blue-800">
          <strong>💡 Tip:</strong> The generated HTML is a complete standalone page. 
          No build process needed - just upload and share the URL!
        </p>
      </div>
    </div>
  );
}

// Made with Bob

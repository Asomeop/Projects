import { useState } from 'react';
import axios from 'axios';

// TypeScript interfaces matching your FastAPI schemas
interface TokenTelemetry {
  estimated_prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  latency_ms: number;
  estimated_cost_usd: number;
  cost_savings_vs_frontier: string;
}

interface RouteResponse {
  status: string;
  cached: boolean;
  routed_tier: string;
  model_name: string;
  response_text: string;
  telemetry: TokenTelemetry;
}

export default function App() {
  const [query, setQuery] = useState('');
  const [forceTier, setForceTier] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RouteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Your live Azure backend URL
  const API_URL = 'https://token-router-backend.purpleisland-17cdd3fa.eastus.azurecontainerapps.io/api/v1/route';

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post<RouteResponse>(API_URL, {
        query,
        force_tier: forceTier || null,
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred connecting to the backend.');
    } finally {
      setLoading(false);
    }
  };

  const handlePreset = (presetText: string) => {
    setQuery(presetText);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans text-gray-800">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Adaptive Token Router & Semantic Gateway</h1>
          <p className="text-gray-600 mt-2">Serverless LLM Proxy & Telemetry Dashboard</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">Prompt Workbench</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Enter Prompt</label>
                <textarea
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={5}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask a question or assign a task..."
                />
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => handlePreset("What is the capital of France?")}
                  className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-1 px-3 rounded-full transition"
                >
                  Simple Prompt
                </button>
                <button
                  type="button"
                  onClick={() => handlePreset("Tell me the capital of France.")}
                  className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-1 px-3 rounded-full transition"
                >
                  Paraphrased (Cache Test)
                </button>
                <button
                  type="button"
                  onClick={() => handlePreset("Derive the mathematical proof for the Pythagorean theorem.")}
                  className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 py-1 px-3 rounded-full transition"
                >
                  Complex Prompt
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tier Override (Optional)</label>
                <select
                  value={forceTier}
                  onChange={(e) => setForceTier(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg bg-white"
                >
                  <option value="">Auto-Route (Default)</option>
                  <option value="tier-1-flash">Force Tier 1 (Flash)</option>
                  <option value="tier-2-frontier">Force Tier 2 (Frontier)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg disabled:opacity-50 transition"
              >
                {loading ? 'Routing Request...' : 'Send Prompt'}
              </button>
            </form>
            
            {error && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-200">
                {error}
              </div>
            )}
          </div>

          <div className="space-y-6">
            
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 min-h-[200px]">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Response</h2>
                {result?.cached && (
                  <span className="bg-green-100 text-green-800 text-xs font-bold px-2.5 py-1 rounded-full border border-green-300">
                    ⚡ Semantic Cache Hit
                  </span>
                )}
              </div>
              
              <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                {result ? result.response_text : <span className="text-gray-400 italic">Awaiting prompt...</span>}
              </div>
            </div>

            {result && (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-xs text-gray-500 font-medium uppercase tracking-wider">Model Used</p>
                  <p className="text-lg font-bold text-gray-900 mt-1">{result.model_name}</p>
                  <p className="text-sm text-gray-500 mt-1">Routed to: {result.routed_tier}</p>
                </div>
                
                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-xs text-gray-500 font-medium uppercase tracking-wider">Latency</p>
                  <p className="text-lg font-bold text-gray-900 mt-1">{result.telemetry.latency_ms} ms</p>
                  <p className="text-sm text-gray-500 mt-1">Total roundtrip</p>
                </div>

                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-xs text-gray-500 font-medium uppercase tracking-wider">Token Usage</p>
                  <p className="text-lg font-bold text-gray-900 mt-1">{result.telemetry.total_tokens}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {result.telemetry.estimated_prompt_tokens} in / {result.telemetry.completion_tokens} out
                  </p>
                </div>

                <div className="bg-green-50 p-4 rounded-xl shadow-sm border border-green-200">
                  <p className="text-xs text-green-700 font-medium uppercase tracking-wider">Cost & Savings</p>
                  <p className="text-lg font-bold text-green-900 mt-1">${result.telemetry.estimated_cost_usd}</p>
                  <p className="text-sm text-green-700 mt-1 font-semibold">
                    Saved {result.telemetry.cost_savings_vs_frontier}
                  </p>
                </div>
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
}
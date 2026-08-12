import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Bot, 
  Database, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  Save, 
  RefreshCw,
  Server
} from 'lucide-react';
import { AppSettingsData } from '../types';
import { api } from '../services/api';

interface SettingsProps {
  settings: AppSettingsData | null;
  onSettingsUpdated: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ settings, onSettingsUpdated }) => {
  const [ollamaHost, setOllamaHost] = useState(settings?.ollama_host || 'http://127.0.0.1:11434');
  const [ollamaModel, setOllamaModel] = useState(settings?.ollama_model || 'qwen2.5:latest');
  const [timeoutSecs, setTimeoutSecs] = useState(settings?.ollama_timeout || 45);
  
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (settings) {
      setOllamaHost(settings.ollama_host);
      setOllamaModel(settings.ollama_model);
      setTimeoutSecs(settings.ollama_timeout);
    }
  }, [settings]);

  const handleTestOllama = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await api.testOllama(ollamaHost);
      setTestResult(res);
    } catch (e: any) {
      setTestResult({ available: false, error: e.message });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      await api.updateSettings({
        ollama_host: ollamaHost,
        ollama_model: ollamaModel,
        ollama_timeout: Number(timeoutSecs)
      });
      setSaveSuccess(true);
      onSettingsUpdated();
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (e) {
      console.error('Failed to save settings', e);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-4xl mx-auto overflow-y-auto h-[calc(100vh-4rem)]">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2.5">
          <SettingsIcon className="w-5 h-5 text-blue-400" />
          <span>System & Model Configuration</span>
        </h2>
        <p className="text-xs text-gray-400 mt-1">
          Configure local Ollama inference settings, timeout policies, and verify administrative privilege level.
        </p>
      </div>

      {/* Privilege Status Card */}
      <div className={`p-5 rounded-2xl border ${
        settings?.is_admin 
          ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300' 
          : 'bg-amber-950/20 border-amber-800/40 text-amber-300'
      }`}>
        <div className="flex items-center gap-3">
          {settings?.is_admin ? (
            <ShieldCheck className="w-6 h-6 text-emerald-400 flex-shrink-0" />
          ) : (
            <ShieldAlert className="w-6 h-6 text-amber-400 flex-shrink-0" />
          )}
          <div>
            <h4 className="text-sm font-bold text-gray-100">
              {settings?.is_admin ? 'Running in Elevated Administrator Mode' : 'Running as Standard User'}
            </h4>
            <p className="text-xs text-gray-400 mt-0.5">
              {settings?.is_admin
                ? 'Direct administrative PowerShell execution is enabled. Service repairs and system scans run without prompts.'
                : 'Elevated actions (e.g. Service control, SFC, DISM) will spawn Windows UAC elevation dialogs.'}
            </p>
          </div>
        </div>
      </div>

      {/* Ollama Configuration Panel */}
      <div className="glass-card p-6 rounded-2xl border border-surface-border space-y-5">
        <div className="flex items-center justify-between border-b border-surface-border pb-4">
          <div className="flex items-center gap-2.5">
            <Bot className="w-5 h-5 text-blue-400" />
            <div>
              <h3 className="text-sm font-bold text-gray-100">Local AI (Ollama) Settings</h3>
              <p className="text-xs text-gray-400">Zero-cost, privacy-preserving local LLM reasoning</p>
            </div>
          </div>
          <button
            onClick={handleTestOllama}
            disabled={isTesting}
            className="px-3.5 py-1.5 rounded-xl bg-surface-elevated hover:bg-gray-700 text-xs font-semibold text-gray-200 border border-surface-border flex items-center gap-1.5 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isTesting ? 'animate-spin text-blue-400' : ''}`} />
            <span>Test Connection</span>
          </button>
        </div>

        {/* Ollama Test Status Result */}
        {testResult && (
          <div className={`p-3.5 rounded-xl border text-xs flex items-center gap-2.5 ${
            testResult.available
              ? 'bg-emerald-950/30 border-emerald-800/40 text-emerald-300'
              : 'bg-yellow-950/30 border-yellow-800/40 text-yellow-300'
          }`}>
            {testResult.available ? <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" /> : <XCircle className="w-4 h-4 text-yellow-400 flex-shrink-0" />}
            <div>
              <span className="font-bold">
                {testResult.available ? 'Ollama Server Connected' : 'Ollama Unreachable'}
              </span>
              <span className="ml-1 text-gray-300">
                {testResult.available 
                  ? `(Found models: ${testResult.models?.join(', ') || 'none'})` 
                  : '- SmartFix will smoothly utilize the deterministic Rule Engine offline.'}
              </span>
            </div>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">
              Ollama Server Endpoint URL
            </label>
            <input
              type="text"
              value={ollamaHost}
              onChange={(e) => setOllamaHost(e.target.value)}
              placeholder="http://127.0.0.1:11434"
              className="w-full bg-surface-elevated border border-surface-border rounded-xl px-4 py-2.5 text-xs text-gray-100 focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                Configured Model Tag
              </label>
              <input
                type="text"
                value={ollamaModel}
                onChange={(e) => setOllamaModel(e.target.value)}
                placeholder="qwen2.5:latest, qwen3:8b, mistral..."
                className="w-full bg-surface-elevated border border-surface-border rounded-xl px-4 py-2.5 text-xs text-gray-100 focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                Inference Timeout (Seconds)
              </label>
              <input
                type="number"
                value={timeoutSecs}
                onChange={(e) => setTimeoutSecs(Number(e.target.value))}
                className="w-full bg-surface-elevated border border-surface-border rounded-xl px-4 py-2.5 text-xs text-gray-100 focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center justify-end gap-3 pt-2">
        {saveSuccess && (
          <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
            <CheckCircle2 className="w-4 h-4" />
            <span>Settings saved successfully</span>
          </span>
        )}
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-glow flex items-center gap-2 transition-all disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          <span>Save Settings</span>
        </button>
      </div>
    </div>
  );
};

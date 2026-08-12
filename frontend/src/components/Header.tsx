import React from 'react';
import { Bot, Cpu, RefreshCw, CheckCircle2, AlertTriangle, XCircle, Wifi } from 'lucide-react';
import { AppSettingsData, SystemHealth } from '../types';

interface HeaderProps {
  currentTab: string;
  settings: AppSettingsData | null;
  health: SystemHealth | null;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  settings,
  health,
  onRefresh,
  isRefreshing
}) => {
  const getTabTitle = () => {
    switch (currentTab) {
      case 'dashboard': return 'System Dashboard';
      case 'diagnose': return 'AI Diagnostics & Troubleshooting';
      case 'health': return 'Windows System Health Monitor';
      case 'repairs': return 'Validated Repair Catalog';
      case 'history': return 'Audit Log & Resolution History';
      case 'demo': return 'Presentation Demo Playground';
      case 'settings': return 'System & Model Settings';
      default: return 'SmartFix AI';
    }
  };

  const ollamaOnline = settings?.ollama_status?.available;

  return (
    <header className="h-16 bg-surface/80 backdrop-blur border-b border-surface-border px-6 flex items-center justify-between z-10 select-none">
      <div>
        <h1 className="text-lg font-bold text-gray-100 flex items-center gap-2">
          {getTabTitle()}
        </h1>
        <p className="text-xs text-gray-400">
          Controlled Windows Diagnostic & Repair Engine
        </p>
      </div>

      <div className="flex items-center gap-4">
        {/* Ollama Status Pill */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
          ollamaOnline 
            ? 'bg-blue-950/40 border-blue-800/50 text-blue-300' 
            : 'bg-yellow-950/40 border-yellow-800/50 text-yellow-300'
        }`}>
          <Bot className="w-3.5 h-3.5" />
          <span>Ollama: {ollamaOnline ? (settings?.ollama_model || 'Online') : 'Rule Fallback Mode'}</span>
          <span className={`w-2 h-2 rounded-full ${ollamaOnline ? 'bg-blue-400 animate-pulse' : 'bg-yellow-400'}`} />
        </div>

        {/* Network & Service status indicators */}
        {health && (
          <div className="hidden md:flex items-center gap-3 text-xs text-gray-400 border-l border-surface-border pl-4">
            <span className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${health.dns_healthy ? 'bg-emerald-400' : 'bg-rose-400'}`} />
              {health.dns_healthy ? 'DNS OK' : 'DNS Issue'}
            </span>
            <span className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${health.failed_services_count === 0 ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              {health.failed_services_count === 0 ? 'Services Normal' : `${health.failed_services_count} Service Alert`}
            </span>
          </div>
        )}

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-lg bg-surface-elevated hover:bg-gray-700 text-gray-300 hover:text-white transition-all border border-surface-border disabled:opacity-50"
          title="Refresh System Data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>
    </header>
  );
};

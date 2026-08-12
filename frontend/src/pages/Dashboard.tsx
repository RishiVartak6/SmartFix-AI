import React from 'react';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  MemoryStick, 
  Wifi, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Stethoscope, 
  ArrowRight,
  ShieldCheck,
  Zap,
  Server
} from 'lucide-react';
import { SystemHealth } from '../types';

interface DashboardProps {
  health: SystemHealth | null;
  isLoading: boolean;
  onNavigateDiagnose: (query?: string) => void;
  onNavigateHealth: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  health,
  isLoading,
  onNavigateDiagnose,
  onNavigateHealth
}) => {
  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'Healthy':
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-700/60 text-emerald-400 text-xs font-semibold">
            <CheckCircle2 className="w-4 h-4" />
            <span>All Systems Healthy</span>
          </div>
        );
      case 'Attention Required':
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950/60 border border-amber-700/60 text-amber-400 text-xs font-semibold">
            <AlertTriangle className="w-4 h-4" />
            <span>Attention Required</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-700/60 text-rose-400 text-xs font-semibold">
            <XCircle className="w-4 h-4" />
            <span>Critical Issues Detected</span>
          </div>
        );
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto overflow-y-auto h-[calc(100vh-4rem)]">
      {/* Hero Welcome & Quick Action Card */}
      <div className="glass-panel p-6 rounded-2xl border border-surface-border bg-gradient-to-r from-surface-elevated/80 via-surface/60 to-blue-950/20 relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-extrabold text-white tracking-tight">
                Windows System Diagnostics
              </h2>
              {health && getStatusBadge(health.health_status)}
            </div>
            <p className="text-sm text-gray-300 leading-relaxed">
              SmartFix AI combines Windows telemetry, deterministic heuristics, and local LLM reasoning to diagnose system failures safely.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigateDiagnose()}
              className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-glow flex items-center gap-2 transition-all group"
            >
              <Stethoscope className="w-4 h-4 group-hover:scale-110 transition-transform" />
              <span>Start Diagnostic Scan</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </div>
        </div>
      </div>

      {/* Real-Time Telemetry Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* CPU Card */}
        <div className="glass-card p-5 rounded-2xl border border-surface-border glass-card-hover space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Processor Load</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
              <Cpu className="w-5 h-5" />
            </div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-white tracking-tight">
              {health ? `${health.cpu_percent}%` : '--'}
            </div>
            <p className="text-xs text-gray-400 mt-1">Multi-core utilization</p>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                (health?.cpu_percent || 0) > 85 ? 'bg-rose-500' : (health?.cpu_percent || 0) > 60 ? 'bg-amber-500' : 'bg-blue-500'
              }`}
              style={{ width: `${Math.min(100, health?.cpu_percent || 0)}%` }}
            />
          </div>
        </div>

        {/* Memory Card */}
        <div className="glass-card p-5 rounded-2xl border border-surface-border glass-card-hover space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">RAM Usage</span>
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
              <MemoryStick className="w-5 h-5" />
            </div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-white tracking-tight">
              {health ? `${health.memory_percent}%` : '--'}
            </div>
            <p className="text-xs text-gray-400 mt-1">Physical memory allocated</p>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                (health?.memory_percent || 0) > 90 ? 'bg-rose-500' : (health?.memory_percent || 0) > 75 ? 'bg-amber-500' : 'bg-purple-500'
              }`}
              style={{ width: `${Math.min(100, health?.memory_percent || 0)}%` }}
            />
          </div>
        </div>

        {/* Disk Card */}
        <div className="glass-card p-5 rounded-2xl border border-surface-border glass-card-hover space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">System Disk (C:)</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <HardDrive className="w-5 h-5" />
            </div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-white tracking-tight">
              {health ? `${health.disk_percent}%` : '--'}
            </div>
            <p className="text-xs text-gray-400 mt-1">Primary drive space used</p>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
            <div 
              className="h-full rounded-full bg-emerald-500 transition-all duration-500"
              style={{ width: `${Math.min(100, health?.disk_percent || 0)}%` }}
            />
          </div>
        </div>

        {/* Network & Services */}
        <div className="glass-card p-5 rounded-2xl border border-surface-border glass-card-hover space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Network & DNS</span>
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
              <Wifi className="w-5 h-5" />
            </div>
          </div>
          <div>
            <div className="text-xl font-bold text-white flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${health?.dns_healthy ? 'bg-emerald-400' : 'bg-rose-500'}`} />
              <span>{health?.dns_healthy ? 'DNS Connected' : 'Resolution Alert'}</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              {health?.uptime_hours ? `System Uptime: ${health.uptime_hours} hrs` : 'Network active'}
            </p>
          </div>
          <div className="text-[11px] text-gray-400 flex items-center justify-between pt-1">
            <span>Critical Services:</span>
            <span className={health?.failed_services_count === 0 ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
              {health?.failed_services_count === 0 ? 'All 12 Running' : `${health?.failed_services_count} Stopped`}
            </span>
          </div>
        </div>
      </div>

      {/* Active Attention Items or System Status Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Attention Items / Health Summary */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-surface-border space-y-4">
          <div className="flex items-center justify-between border-b border-surface-border pb-4">
            <div className="flex items-center gap-2.5">
              <Activity className="w-5 h-5 text-blue-400" />
              <h3 className="font-bold text-gray-100">Live Health Findings</h3>
            </div>
            <button
              onClick={onNavigateHealth}
              className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1"
            >
              <span>View All Subsystems</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {health?.attention_reasons && health.attention_reasons.length > 0 ? (
            <div className="space-y-3">
              {health.attention_reasons.map((reason, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-800/30 flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-semibold text-gray-200">{reason}</p>
                      <p className="text-[11px] text-gray-400 mt-0.5">Automated telemetry flagged this condition during live sampling.</p>
                    </div>
                  </div>
                  <button
                    onClick={() => onNavigateDiagnose(reason)}
                    className="px-3 py-1.5 rounded-lg bg-blue-600/80 hover:bg-blue-600 text-white text-xs font-medium flex-shrink-0 transition-colors"
                  >
                    Diagnose
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center space-y-2">
              <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
              <p className="text-sm font-semibold text-gray-200">No Immediate System Anomalies Detected</p>
              <p className="text-xs text-gray-400 max-w-md mx-auto">
                Windows update services, print spooler, audio endpoints, and DNS lookups are functioning normally.
              </p>
            </div>
          )}
        </div>

        {/* Right 1 Col: Quick Diagnostic Assistant */}
        <div className="glass-card p-6 rounded-2xl border border-surface-border space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-blue-400">
              <Zap className="w-5 h-5" />
              <h3 className="font-bold text-gray-100">Describe a Problem</h3>
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">
              Facing audio failures, printer queue halts, or network issues? Type your issue below for AI-assisted root cause analysis.
            </p>
          </div>

          <div className="space-y-2 pt-4">
            <button
              onClick={() => onNavigateDiagnose('My sound is muted and audio service is not working')}
              className="w-full text-left p-2.5 rounded-xl bg-surface-elevated/70 hover:bg-surface-elevated text-xs text-gray-300 hover:text-white border border-surface-border transition-all flex items-center justify-between"
            >
              <span>"Audio is muted / not playing"</span>
              <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
            </button>
            <button
              onClick={() => onNavigateDiagnose('Print Spooler service stopped and printer is offline')}
              className="w-full text-left p-2.5 rounded-xl bg-surface-elevated/70 hover:bg-surface-elevated text-xs text-gray-300 hover:text-white border border-surface-border transition-all flex items-center justify-between"
            >
              <span>"Printer offline / Spooler stopped"</span>
              <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
            </button>
            <button
              onClick={() => onNavigateDiagnose('Cannot resolve websites and DNS error')}
              className="w-full text-left p-2.5 rounded-xl bg-surface-elevated/70 hover:bg-surface-elevated text-xs text-gray-300 hover:text-white border border-surface-border transition-all flex items-center justify-between"
            >
              <span>"Cannot load websites / DNS error"</span>
              <ArrowRight className="w-3.5 h-3.5 text-blue-400" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

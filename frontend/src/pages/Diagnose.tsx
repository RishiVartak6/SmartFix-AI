import React, { useState, useEffect } from 'react';
import { 
  Stethoscope, 
  Sparkles, 
  Send, 
  CheckCircle2, 
  AlertTriangle, 
  Wrench, 
  ShieldCheck, 
  Info, 
  Layers,
  ArrowRight,
  Terminal,
  Activity
} from 'lucide-react';
import { DiagnosisItem, DiagnosisSessionResponse } from '../types';
import { api } from '../services/api';

interface DiagnoseProps {
  initialQuery?: string;
  onRequestRepair: (diagnosis: DiagnosisItem) => void;
}

export const Diagnose: React.FC<DiagnoseProps> = ({ initialQuery, onRequestRepair }) => {
  const [activeMode, setActiveMode] = useState<'scan' | 'describe'>('scan');
  const [userQuery, setUserQuery] = useState(initialQuery || '');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState<string>('');
  const [sessionResult, setSessionResult] = useState<DiagnosisSessionResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (initialQuery) {
      setUserQuery(initialQuery);
      setActiveMode('describe');
      runDiagnosis('user_query', initialQuery);
    }
  }, [initialQuery]);

  const runDiagnosis = async (mode: 'full_scan' | 'user_query', query?: string) => {
    setIsAnalyzing(true);
    setErrorMsg(null);
    setSessionResult(null);

    // Dynamic analysis steps for technical impressiveness and clarity
    setAnalysisStep('Querying Windows Event Viewer logs (Application & System)...');
    await new Promise(r => setTimeout(r, 400));
    setAnalysisStep('Inspecting Windows Services & Process resource consumption...');
    await new Promise(r => setTimeout(r, 400));
    setAnalysisStep('Evaluating Deterministic Heuristic Rules & AI Reasoning Model...');

    try {
      const res = await api.diagnose(mode, query);
      setSessionResult(res);
    } catch (err: any) {
      setErrorMsg(err?.message || 'Diagnostic scan failed to communicate with backend.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'low':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-950/60 border border-blue-700/60 text-blue-400">Low Severity</span>;
      case 'high':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-950/60 border border-rose-700/60 text-rose-400">High Severity</span>;
      case 'critical':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-950/80 border border-rose-600 text-rose-300 font-bold">Critical</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-950/60 border border-amber-700/60 text-amber-400">Medium Severity</span>;
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-6xl mx-auto overflow-y-auto h-[calc(100vh-4rem)]">
      {/* Top Selector Card */}
      <div className="glass-panel p-6 rounded-2xl border border-surface-border space-y-5">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2.5">
            <Stethoscope className="w-5 h-5 text-blue-400" />
            <span>AI Diagnostic Engine</span>
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Choose whether to perform an automated full system scan or describe a specific problem.
          </p>
        </div>

        {/* Mode Switch Tabs */}
        <div className="flex items-center gap-2 p-1 rounded-xl bg-surface-elevated/70 border border-surface-border w-fit">
          <button
            onClick={() => setActiveMode('scan')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeMode === 'scan'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Option A: Automated Full System Scan
          </button>
          <button
            onClick={() => setActiveMode('describe')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeMode === 'describe'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Option B: Describe My Problem
          </button>
        </div>

        {/* Option A: Full Scan Trigger */}
        {activeMode === 'scan' && (
          <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-900/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <p className="text-sm font-semibold text-gray-200">Run Complete Diagnostic Inspection</p>
              <p className="text-xs text-gray-400">
                Samples 12+ critical Windows services, DNS resolution, system memory/CPU anomalies, and recent error logs.
              </p>
            </div>
            <button
              onClick={() => runDiagnosis('full_scan')}
              disabled={isAnalyzing}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-glow flex items-center gap-2 transition-all flex-shrink-0 disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>Scan System Now</span>
            </button>
          </div>
        )}

        {/* Option B: Describe My Problem */}
        {activeMode === 'describe' && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (userQuery.trim()) runDiagnosis('user_query', userQuery.trim());
            }}
            className="space-y-3"
          >
            <div className="relative">
              <input
                type="text"
                value={userQuery}
                onChange={(e) => setUserQuery(e.target.value)}
                placeholder="e.g., 'My printer is not printing and queue is stuck', 'Windows update fails to download'..."
                className="w-full bg-surface-elevated/90 border border-surface-border rounded-xl px-4 py-3.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={isAnalyzing || !userQuery.trim()}
                className="absolute right-2 top-2 bottom-2 px-4 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Diagnose</span>
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Analyzing Progress State */}
      {isAnalyzing && (
        <div className="glass-card p-8 rounded-2xl border border-blue-500/30 text-center space-y-4 animate-in fade-in duration-300">
          <div className="relative inline-block">
            <div className="w-16 h-16 rounded-full border-4 border-blue-500/20 border-t-blue-500 animate-spin mx-auto" />
            <Sparkles className="w-6 h-6 text-blue-400 absolute inset-0 m-auto" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-gray-100">Analyzing System Telemetry & Logs...</h3>
            <p className="text-xs text-blue-400 font-mono animate-pulse">{analysisStep}</p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/50 text-rose-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Diagnosis Results Cards */}
      {sessionResult && !isAnalyzing && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-gray-100 flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-400" />
              <span>Diagnosis Findings ({sessionResult.diagnoses.length})</span>
            </h3>
            <span className="text-xs text-gray-400 font-mono">
              Session ID: {sessionResult.session_id.substring(0, 8)}...
            </span>
          </div>

          <div className="space-y-4">
            {sessionResult.diagnoses.map((diag) => {
              const confPct = Math.round(diag.confidence * 100);
              return (
                <div 
                  key={diag.id} 
                  className="glass-card p-6 rounded-2xl border border-surface-border glass-card-hover space-y-4"
                >
                  {/* Card Header */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-surface-border pb-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-3">
                        <h4 className="text-lg font-bold text-gray-100">{diag.problem}</h4>
                        {getSeverityBadge(diag.severity)}
                      </div>
                      <p className="text-xs text-gray-400">Root cause identified via telemetry & rule correlation</p>
                    </div>

                    {/* Confidence Meter */}
                    <div className="flex items-center gap-3 bg-surface-elevated/70 px-3.5 py-1.5 rounded-xl border border-surface-border flex-shrink-0">
                      <div className="text-right">
                        <div className="text-[10px] uppercase font-semibold text-gray-400">Confidence</div>
                        <div className={`text-sm font-bold ${confPct >= 80 ? 'text-emerald-400' : confPct >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                          {confPct}% ({diag.confidence_level.toUpperCase()})
                        </div>
                      </div>
                      <div className="w-16 bg-gray-800 rounded-full h-2 overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${confPct >= 80 ? 'bg-emerald-500' : confPct >= 50 ? 'bg-amber-500' : 'bg-rose-500'}`}
                          style={{ width: `${confPct}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Probable Root Cause & Explanation */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-3.5 rounded-xl bg-surface-elevated/40 border border-surface-border space-y-1.5">
                      <span className="text-xs font-semibold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
                        <Terminal className="w-3.5 h-3.5" />
                        Probable Technical Root Cause
                      </span>
                      <p className="text-xs text-gray-200 leading-relaxed font-mono">{diag.probable_root_cause}</p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-surface-elevated/40 border border-surface-border space-y-1.5">
                      <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                        <Info className="w-3.5 h-3.5" />
                        Plain Explanation
                      </span>
                      <p className="text-xs text-gray-300 leading-relaxed">{diag.explanation}</p>
                    </div>
                  </div>

                  {/* Evidence Items */}
                  {diag.evidence.length > 0 && (
                    <div className="space-y-1.5">
                      <span className="text-xs font-semibold text-gray-400">Correlated Diagnostic Evidence:</span>
                      <div className="flex flex-wrap gap-1.5">
                        {diag.evidence.map((ev, i) => (
                          <span key={i} className="text-xs bg-gray-800 border border-gray-700 text-gray-300 px-2.5 py-1 rounded-lg flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                            {ev}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Area / Safe Repair Gate */}
                  {diag.recommended_repair_id ? (
                    <div className="pt-2 flex items-center justify-between border-t border-surface-border">
                      <div className="text-xs text-gray-400 flex items-center gap-1.5">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        <span>Recommended Validated Repair: <strong className="text-gray-200">{diag.recommended_repair_id}</strong></span>
                      </div>
                      <button
                        onClick={() => onRequestRepair(diag)}
                        className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-glow flex items-center gap-2 transition-all"
                      >
                        <Wrench className="w-3.5 h-3.5" />
                        <span>Review & Approve Repair</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ) : (
                    <div className="pt-2 text-xs text-gray-400 italic">
                      No automated script execution required for this condition.
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

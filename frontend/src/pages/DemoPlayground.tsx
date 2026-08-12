import React, { useState } from 'react';
import { 
  FlaskConical, 
  Play, 
  RotateCcw, 
  AlertTriangle, 
  CheckCircle2, 
  Printer, 
  Clock, 
  Bluetooth, 
  Wifi,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

interface DemoProps {
  onNavigateDiagnose: (query?: string) => void;
}

export const DemoPlayground: React.FC<DemoProps> = ({ onNavigateDiagnose }) => {
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<any>(null);

  const handleSimulate = async (faultType: string) => {
    setActiveAction(faultType);
    setFeedback(null);
    try {
      const res = await api.simulateFault(faultType);
      setFeedback({ type: 'fault', data: res });
    } catch (e: any) {
      setFeedback({ type: 'error', error: e.message });
    } finally {
      setActiveAction(null);
    }
  };

  const handleRestore = async () => {
    setActiveAction('restore');
    setFeedback(null);
    try {
      const res = await api.restoreAllDemoServices();
      setFeedback({ type: 'restore', data: res });
    } catch (e: any) {
      setFeedback({ type: 'error', error: e.message });
    } finally {
      setActiveAction(null);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-5xl mx-auto overflow-y-auto h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl border border-surface-border bg-gradient-to-r from-purple-950/20 via-surface-elevated/40 to-blue-950/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/30 text-purple-400 flex items-center justify-center">
            <FlaskConical className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-100">Viva & Presentation Demo Playground</h2>
            <p className="text-xs text-gray-300 mt-0.5">
              Simulate real Windows fault conditions with 1-click to showcase the end-to-end Diagnose → AI Reasoning → Approval → Validated Fix → Verification loop during reviews.
            </p>
          </div>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedback && (
        <div className={`p-4 rounded-xl border text-xs flex items-center justify-between gap-3 ${
          feedback.type === 'error'
            ? 'bg-rose-950/30 border-rose-800/40 text-rose-300'
            : 'bg-emerald-950/30 border-emerald-800/40 text-emerald-300'
        }`}>
          <div className="flex items-center gap-2.5">
            {feedback.type === 'error' ? <AlertTriangle className="w-4 h-4 text-rose-400" /> : <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
            <div>
              <p className="font-bold">{feedback.data?.message || feedback.error}</p>
              {feedback.data?.output && <p className="font-mono text-[11px] text-gray-300 mt-0.5">{feedback.data.output}</p>}
            </div>
          </div>
          {feedback.type === 'fault' && (
            <button
              onClick={() => onNavigateDiagnose()}
              className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-all shadow-sm"
            >
              <span>Diagnose Now</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Demo Scenario Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Scenario 1: Print Spooler */}
        <div className="glass-card p-5 rounded-2xl border border-surface-border space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-400 text-xs font-bold uppercase tracking-wider">
              <Printer className="w-4 h-4" />
              <span>Scenario 1: Print Spooler Failure</span>
            </div>
            <span className="text-[10px] bg-blue-950 text-blue-400 px-2 py-0.5 rounded font-mono">Service Fault</span>
          </div>

          <p className="text-xs text-gray-300 leading-relaxed">
            Stops the Windows <code>Spooler</code> service to simulate a blocked printer queue. SmartFix will identify the stopped service, explain why printing is offline, request approval, and restart it.
          </p>

          <div className="pt-2 border-t border-surface-border flex items-center justify-end">
            <button
              onClick={() => handleSimulate('stop_print_spooler')}
              disabled={activeAction !== null}
              className="px-4 py-2 rounded-xl bg-surface-elevated hover:bg-rose-900/40 text-gray-200 hover:text-rose-300 text-xs font-semibold border border-surface-border hover:border-rose-700 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Simulate Stopped Spooler</span>
            </button>
          </div>
        </div>

        {/* Scenario 2: Windows Time Service */}
        <div className="glass-card p-5 rounded-2xl border border-surface-border space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
              <Clock className="w-4 h-4" />
              <span>Scenario 2: Time Service Halting</span>
            </div>
            <span className="text-[10px] bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded font-mono">Time Sync</span>
          </div>

          <p className="text-xs text-gray-300 leading-relaxed">
            Stops <code>W32Time</code> service. SmartFix detects clock drift risk, alerts that HTTPS security handshakes can fail, and offers validated time service resync.
          </p>

          <div className="pt-2 border-t border-surface-border flex items-center justify-end">
            <button
              onClick={() => handleSimulate('stop_time_service')}
              disabled={activeAction !== null}
              className="px-4 py-2 rounded-xl bg-surface-elevated hover:bg-rose-900/40 text-gray-200 hover:text-rose-300 text-xs font-semibold border border-surface-border hover:border-rose-700 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Simulate Stopped Time Svc</span>
            </button>
          </div>
        </div>

        {/* Scenario 3: Bluetooth Service */}
        <div className="glass-card p-5 rounded-2xl border border-surface-border space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-purple-400 text-xs font-bold uppercase tracking-wider">
              <Bluetooth className="w-4 h-4" />
              <span>Scenario 3: Bluetooth Peripheral Drop</span>
            </div>
            <span className="text-[10px] bg-purple-950 text-purple-400 px-2 py-0.5 rounded font-mono">Device Stack</span>
          </div>

          <p className="text-xs text-gray-300 leading-relaxed">
            Stops <code>bthserv</code> service. SmartFix diagnoses the missing peripheral communication stack and recommends the safe restart workflow.
          </p>

          <div className="pt-2 border-t border-surface-border flex items-center justify-end">
            <button
              onClick={() => handleSimulate('stop_bluetooth_service')}
              disabled={activeAction !== null}
              className="px-4 py-2 rounded-xl bg-surface-elevated hover:bg-rose-900/40 text-gray-200 hover:text-rose-300 text-xs font-semibold border border-surface-border hover:border-rose-700 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Simulate Stopped Bluetooth</span>
            </button>
          </div>
        </div>

        {/* Scenario 4: DNS Diagnostic Flush Test */}
        <div className="glass-card p-5 rounded-2xl border border-surface-border space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase tracking-wider">
              <Wifi className="w-4 h-4" />
              <span>Scenario 4: DNS Cache Refresh Test</span>
            </div>
            <span className="text-[10px] bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded font-mono">Network</span>
          </div>

          <p className="text-xs text-gray-300 leading-relaxed">
            Tests the DNS cache flush pipeline and runs immediate socket verification against public authoritative nameservers.
          </p>

          <div className="pt-2 border-t border-surface-border flex items-center justify-end">
            <button
              onClick={() => handleSimulate('flush_dns_test')}
              disabled={activeAction !== null}
              className="px-4 py-2 rounded-xl bg-surface-elevated hover:bg-blue-600 text-gray-200 hover:text-white text-xs font-semibold border border-surface-border hover:border-blue-500 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Test DNS Flush & Verify</span>
            </button>
          </div>
        </div>
      </div>

      {/* Global Restore Button */}
      <div className="p-5 rounded-2xl bg-surface-elevated/40 border border-surface-border flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-gray-100">Reset & Restore All Demonstration Services</h4>
          <p className="text-xs text-gray-400 mt-0.5">Ensures all simulated stopped services (Spooler, W32Time, bthserv) are restarted and healthy.</p>
        </div>
        <button
          onClick={handleRestore}
          disabled={activeAction !== null}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-glow flex items-center gap-2 transition-all disabled:opacity-50"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Restore All Services</span>
        </button>
      </div>
    </div>
  );
};

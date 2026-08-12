import React from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Terminal, 
  Clock, 
  ShieldCheck, 
  Sparkles, 
  ArrowRight, 
  X,
  RotateCcw
} from 'lucide-react';
import { RepairExecutionResult } from '../types';

interface ExecutionModalProps {
  result: RepairExecutionResult | null;
  isLoading: boolean;
  onClose: () => void;
  onRediagnose?: () => void;
}

export const ExecutionModal: React.FC<ExecutionModalProps> = ({
  result,
  isLoading,
  onClose,
  onRediagnose
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-surface border border-surface-border rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden glass-panel flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between bg-surface-elevated/40">
          <div className="flex items-center gap-2.5">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
              isLoading 
                ? 'bg-blue-500/20 text-blue-400' 
                : result?.verification_success 
                  ? 'bg-emerald-500/20 text-emerald-400' 
                  : 'bg-rose-500/20 text-rose-400'
            }`}>
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
              ) : result?.verification_success ? (
                <CheckCircle2 className="w-5 h-5" />
              ) : (
                <XCircle className="w-5 h-5" />
              )}
            </div>
            <div>
              <h3 className="text-base font-bold text-gray-100">
                {isLoading ? 'Executing Repair Workflow...' : result?.verification_success ? 'Repair Successfully Verified' : 'Repair Completed (Action Required)'}
              </h3>
              <p className="text-xs text-gray-400">
                {isLoading ? 'Controlled script running in background' : `Execution time: ${result?.duration_ms || 0}ms`}
              </p>
            </div>
          </div>
          {!isLoading && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-200 p-1.5 rounded-lg hover:bg-gray-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4 overflow-y-auto flex-1">
          {isLoading ? (
            <div className="py-12 flex flex-col items-center justify-center text-center space-y-4">
              <div className="relative">
                <div className="w-16 h-16 rounded-full border-4 border-blue-500/20 border-t-blue-500 animate-spin" />
                <Sparkles className="w-6 h-6 text-blue-400 absolute inset-0 m-auto" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-gray-200">Executing Predefined PowerShell Script...</p>
                <p className="text-xs text-gray-400">Capturing output stream & preparing verification test</p>
              </div>
            </div>
          ) : result ? (
            <>
              {/* Verification Outcome Banner */}
              <div className={`p-4 rounded-xl border flex items-start gap-3.5 ${
                result.verification_success
                  ? 'bg-emerald-950/30 border-emerald-800/40 text-emerald-200'
                  : 'bg-rose-950/30 border-rose-800/40 text-rose-200'
              }`}>
                {result.verification_success ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-6 h-6 text-rose-400 flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <h4 className="text-sm font-bold text-gray-100">
                    {result.verification_success ? 'Problem Successfully Resolved' : 'Repair Unsuccessful — Additional Steps Needed'}
                  </h4>
                  <p className="text-xs mt-1 text-gray-300 leading-relaxed">
                    {result.verification_message || (result.verification_success ? "Post-repair verification check passed." : "Verification criteria was not fully met.")}
                  </p>
                </div>
              </div>

              {/* Execution Output Console */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-medium text-gray-400">
                  <span className="flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5 text-gray-400" />
                    PowerShell Execution Output
                  </span>
                  <span>Exit Code: {result.error_message ? 'Failed' : '0 (OK)'}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-black/70 border border-gray-800 font-mono text-xs text-emerald-400 max-h-40 overflow-y-auto whitespace-pre-wrap select-text">
                  {result.execution_output || (result.error_message ? `Error: ${result.error_message}` : "[Execution completed with no standard output]")}
                </div>
              </div>

              {/* Follow-up Next Step Recommendation if Failed */}
              {!result.verification_success && (
                <div className="p-3.5 rounded-xl bg-surface-elevated/60 border border-surface-border text-xs space-y-1.5">
                  <span className="font-semibold text-amber-400">Next Recommended Step:</span>
                  <p className="text-gray-300">
                    If this service remains blocked, run a deeper <strong>System File Checker (SFC)</strong> scan or verify that dependent driver components are active in Device Manager.
                  </p>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-surface-border bg-surface-elevated/40 flex items-center justify-end gap-3">
          {!isLoading && (
            <>
              {onRediagnose && (
                <button
                  onClick={() => {
                    onClose();
                    onRediagnose();
                  }}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-300 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 flex items-center gap-1.5 transition-all"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Run New Scan</span>
                </button>
              )}
              <button
                onClick={onClose}
                className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-glow transition-all"
              >
                Close & Return to Dashboard
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle, X, Wrench, Sparkles, Lock } from 'lucide-react';
import { DiagnosisItem, RepairCatalogItem } from '../types';

interface ApprovalModalProps {
  diagnosis: DiagnosisItem;
  repair: RepairCatalogItem | null;
  isAdmin: boolean;
  onApprove: () => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({
  diagnosis,
  repair,
  isAdmin,
  onApprove,
  onCancel,
  isSubmitting = false
}) => {
  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'low':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/70 border border-emerald-700/60 text-emerald-400">Low Risk</span>;
      case 'medium':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-950/70 border border-amber-700/60 text-amber-400">Medium Risk</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-950/70 border border-rose-700/60 text-rose-400">High Risk</span>;
    }
  };

  const confidencePercent = Math.round(diagnosis.confidence * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-surface border border-surface-border rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden glass-panel">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between bg-surface-elevated/40">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-gray-100">Repair Approval Required</h3>
              <p className="text-xs text-gray-400">Controlled Execution Safety Gate</p>
            </div>
          </div>
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="text-gray-400 hover:text-gray-200 p-1.5 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          {/* Problem & Root Cause Box */}
          <div className="p-4 rounded-xl bg-surface-elevated/50 border border-surface-border/80 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-blue-400">Detected Problem</span>
              <span className="text-xs font-medium text-gray-400">AI Confidence: {confidencePercent}%</span>
            </div>
            <p className="text-sm font-semibold text-gray-100">{diagnosis.problem}</p>
            <p className="text-xs text-gray-300 leading-relaxed">{diagnosis.probable_root_cause}</p>
          </div>

          {/* Proposed Repair Details */}
          <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-900/40 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold uppercase tracking-wider">
                <Wrench className="w-4 h-4" />
                <span>Proposed Repair Workflow</span>
              </div>
              {repair && getRiskBadge(repair.risk)}
            </div>

            <div>
              <h4 className="text-sm font-bold text-gray-100">
                {repair ? repair.name : diagnosis.recommended_repair_id}
              </h4>
              <p className="text-xs text-gray-300 mt-1 leading-relaxed">
                {repair ? repair.description : diagnosis.explanation}
              </p>
            </div>

            {/* Admin Privilege Notification */}
            {repair?.requires_admin && (
              <div className="flex items-center gap-2 p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/40 text-amber-300 text-xs">
                <Lock className="w-4 h-4 flex-shrink-0 text-amber-400" />
                <span>
                  {isAdmin 
                    ? "This repair requires administrator privileges (Granted)." 
                    : "This repair requires administrator privileges. Windows UAC elevation may trigger."}
                </span>
              </div>
            )}
          </div>

          {/* Evidence Snippet */}
          {diagnosis.evidence.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-gray-400">Supporting System Evidence:</span>
              <div className="flex flex-wrap gap-1.5">
                {diagnosis.evidence.map((ev, idx) => (
                  <span key={idx} className="text-[11px] bg-gray-800/80 border border-gray-700 text-gray-300 px-2 py-0.5 rounded-md">
                    {ev}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer / Buttons */}
        <div className="px-6 py-4 border-t border-surface-border bg-surface-elevated/40 flex items-center justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-xl text-sm font-medium text-gray-300 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 transition-all disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onApprove}
            disabled={isSubmitting}
            className="px-5 py-2 rounded-xl text-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-glow flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {isSubmitting ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Authorizing...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" />
                <span>Approve & Execute Repair</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

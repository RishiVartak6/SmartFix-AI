import React, { useState, useEffect } from 'react';
import { 
  History as HistoryIcon, 
  CheckCircle2, 
  XCircle, 
  Search, 
  Trash2, 
  Terminal, 
  Clock,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { HistoryResponse } from '../types';
import { api } from '../services/api';

export const History: React.FC = () => {
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedRecord, setSelectedRecord] = useState<any | null>(null);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const data = await api.getHistory(50);
      setHistory(data);
    } catch (e) {
      console.error('Failed to load history', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear diagnostic and repair history records from SQLite database?')) {
      try {
        await api.clearHistory();
        await loadHistory();
        setSelectedRecord(null);
      } catch (e) {
        console.error('Failed to clear history', e);
      }
    }
  };

  const filteredRepairs = (history?.repairs || []).filter(r => 
    r.repair_name.toLowerCase().includes(search.toLowerCase()) ||
    r.repair_id.toLowerCase().includes(search.toLowerCase()) ||
    (r.verification_message && r.verification_message.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto overflow-y-auto h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2.5">
            <HistoryIcon className="w-5 h-5 text-blue-400" />
            <span>Audit Trail & Repair History</span>
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Permanent SQLite logs of user approvals, script outputs, and post-repair verifications.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadHistory}
            disabled={isLoading}
            className="p-2 rounded-xl bg-surface-elevated hover:bg-gray-700 text-gray-300 border border-surface-border transition-all"
            title="Refresh History"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
          <button
            onClick={handleClearHistory}
            className="px-3.5 py-2 rounded-xl bg-surface-elevated hover:bg-rose-900/50 text-gray-300 hover:text-rose-300 text-xs font-semibold border border-surface-border hover:border-rose-700 flex items-center gap-1.5 transition-all"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History</span>
          </button>
        </div>
      </div>

      {/* Filter / Search */}
      <div className="relative max-w-sm w-full">
        <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by repair name, ID, or result..."
          className="w-full bg-surface-elevated border border-surface-border rounded-xl pl-9 pr-4 py-2 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Main Content: Table & Detail Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Table List (2 Cols) */}
        <div className="lg:col-span-2 glass-card rounded-2xl border border-surface-border overflow-hidden">
          <div className="p-4 border-b border-surface-border bg-surface-elevated/40 flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-300">Executed Repairs ({filteredRepairs.length})</span>
            <span className="text-xs text-gray-400">Total sessions recorded: {history?.total_sessions || 0}</span>
          </div>

          <div className="divide-y divide-surface-border max-h-[520px] overflow-y-auto">
            {filteredRepairs.length > 0 ? (
              filteredRepairs.map((r) => (
                <div
                  key={r.id}
                  onClick={() => setSelectedRecord(r)}
                  className={`p-4 hover:bg-surface-elevated/40 cursor-pointer transition-colors flex items-center justify-between gap-4 ${
                    selectedRecord?.id === r.id ? 'bg-blue-600/10 border-l-2 border-blue-500' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {r.verification_success ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-gray-100">{r.repair_name}</span>
                        <span className="text-[10px] text-gray-400 font-mono">({r.repair_id})</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">{r.verification_message}</p>
                    </div>
                  </div>

                  <div className="text-right flex-shrink-0 text-xs">
                    <span className="font-mono text-gray-400 text-[11px] block">{r.timestamp}</span>
                    <span className="text-[10px] text-gray-500">{r.duration_ms}ms</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-12 text-center text-xs text-gray-400">
                No repair execution records found.
              </div>
            )}
          </div>
        </div>

        {/* Detail Panel (1 Col) */}
        <div className="glass-card p-6 rounded-2xl border border-surface-border space-y-4">
          <h3 className="text-sm font-bold text-gray-100 flex items-center gap-2 border-b border-surface-border pb-3">
            <Terminal className="w-4 h-4 text-blue-400" />
            <span>Execution Audit Details</span>
          </h3>

          {selectedRecord ? (
            <div className="space-y-4 text-xs">
              <div>
                <span className="text-gray-400">Repair Workflow:</span>
                <p className="text-sm font-bold text-gray-100">{selectedRecord.repair_name}</p>
                <p className="text-gray-400 font-mono text-[11px]">ID: {selectedRecord.repair_id}</p>
              </div>

              <div>
                <span className="text-gray-400">Status & Verification:</span>
                <div className="mt-1 p-2.5 rounded-lg bg-surface-elevated border border-surface-border">
                  <p className={`font-semibold ${selectedRecord.verification_success ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {selectedRecord.verification_success ? 'Verification Succeeded' : 'Verification Unmet'}
                  </p>
                  <p className="text-gray-300 mt-0.5">{selectedRecord.verification_message}</p>
                </div>
              </div>

              <div>
                <span className="text-gray-400">Execution Output:</span>
                <div className="mt-1 p-3 rounded-xl bg-black/70 border border-gray-800 font-mono text-[11px] text-emerald-400 max-h-40 overflow-y-auto whitespace-pre-wrap select-text">
                  {selectedRecord.execution_output || "[No output text generated]"}
                </div>
              </div>

              <div className="pt-2 border-t border-surface-border flex items-center justify-between text-gray-400 text-[11px]">
                <span>Recorded: {selectedRecord.timestamp}</span>
                <span>Duration: {selectedRecord.duration_ms} ms</span>
              </div>
            </div>
          ) : (
            <div className="py-16 text-center text-xs text-gray-500 space-y-2">
              <Clock className="w-8 h-8 mx-auto text-gray-600" />
              <p>Select any repair log to inspect complete verification and PowerShell stdout data.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

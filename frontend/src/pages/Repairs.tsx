import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  ShieldCheck, 
  Lock, 
  CheckCircle, 
  Search, 
  Terminal, 
  AlertTriangle,
  Play,
  Layers
} from 'lucide-react';
import { RepairCatalogItem } from '../types';
import { api } from '../services/api';

interface RepairsProps {
  isAdmin: boolean;
  onExecuteManualRepair: (repair: RepairCatalogItem) => void;
}

export const Repairs: React.FC<RepairsProps> = ({ isAdmin, onExecuteManualRepair }) => {
  const [repairs, setRepairs] = useState<RepairCatalogItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  useEffect(() => {
    loadRepairs();
  }, []);

  const loadRepairs = async () => {
    setIsLoading(true);
    try {
      const data = await api.getRepairsCatalog();
      setRepairs(data.catalog);
    } catch (e) {
      console.error('Failed to load repair catalog', e);
    } finally {
      setIsLoading(false);
    }
  };

  const categories = ['All', ...Array.from(new Set(repairs.map(r => r.category)))];

  const filteredRepairs = repairs.filter(r => {
    const matchesCategory = selectedCategory === 'All' || r.category === selectedCategory;
    const matchesSearch = r.name.toLowerCase().includes(search.toLowerCase()) ||
                          r.description.toLowerCase().includes(search.toLowerCase()) ||
                          r.id.toLowerCase().includes(search.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'low':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/70 border border-emerald-700/60 text-emerald-400">LOW RISK</span>;
      case 'medium':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-950/70 border border-amber-700/60 text-amber-400">MEDIUM RISK</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-950/70 border border-rose-700/60 text-rose-400">HIGH RISK</span>;
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto overflow-y-auto h-[calc(100vh-4rem)]">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2.5">
            <Wrench className="w-5 h-5 text-blue-400" />
            <span>Validated Repair Catalog ({repairs.length})</span>
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Predefined, deterministic PowerShell repair scripts strictly protected by the allowlist registry.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative max-w-xs w-full">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter repairs..."
            className="w-full bg-surface-elevated border border-surface-border rounded-xl pl-9 pr-4 py-2 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap items-center gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-surface-elevated text-gray-400 hover:text-gray-200 border border-surface-border'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Repair Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredRepairs.map((repair) => (
          <div
            key={repair.id}
            className="glass-card p-5 rounded-2xl border border-surface-border glass-card-hover flex flex-col justify-between space-y-4"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-semibold text-blue-400 uppercase tracking-wider bg-blue-950/40 px-2 py-0.5 rounded">
                  {repair.category}
                </span>
                <div className="flex items-center gap-2">
                  {repair.requires_admin && (
                    <span title="Requires Administrator Rights" className="text-amber-400 flex items-center gap-1 text-[10px] font-mono bg-amber-950/60 px-1.5 py-0.5 rounded border border-amber-800/40">
                      <Lock className="w-3 h-3" />
                      ADMIN
                    </span>
                  )}
                  {getRiskBadge(repair.risk)}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-bold text-gray-100">{repair.name}</h4>
                <p className="text-xs text-gray-400 font-mono mt-0.5">ID: {repair.id}</p>
                <p className="text-xs text-gray-300 mt-2 leading-relaxed line-clamp-3">
                  {repair.description}
                </p>
              </div>
            </div>

            <div className="pt-3 border-t border-surface-border flex items-center justify-between">
              <div className="text-[11px] text-gray-500 font-mono">
                Verifier: {repair.verification.replace('verify_', '')}
              </div>
              <button
                onClick={() => onExecuteManualRepair(repair)}
                className="px-3.5 py-1.5 rounded-lg bg-surface-elevated hover:bg-blue-600 text-gray-200 hover:text-white text-xs font-semibold border border-surface-border hover:border-blue-500 flex items-center gap-1.5 transition-all shadow-sm"
              >
                <Play className="w-3 h-3" />
                <span>Execute</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

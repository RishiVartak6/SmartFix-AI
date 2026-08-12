import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Server, 
  FileText, 
  Cpu, 
  Wifi, 
  AlertCircle, 
  CheckCircle2, 
  XCircle, 
  Search, 
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { EventLogItem, ProcessItem, NetworkInfo } from '../types';

export const SystemHealth: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'services' | 'events' | 'processes' | 'network'>('services');
  const [servicesData, setServicesData] = useState<any>(null);
  const [eventsData, setEventsData] = useState<EventLogItem[]>([]);
  const [processesData, setProcessesData] = useState<{ top_by_cpu: ProcessItem[]; top_by_ram: ProcessItem[] } | null>(null);
  const [networkData, setNetworkData] = useState<NetworkInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState('');

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [srv, ev, proc, net] = await Promise.all([
        api.getServices(),
        api.getEvents(48, 40),
        api.getProcesses(20),
        api.getNetwork()
      ]);
      setServicesData(srv);
      setEventsData(ev);
      setProcessesData(proc);
      setNetworkData(net);
    } catch (e) {
      console.error('Failed to load system telemetry', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredServices = (servicesData?.critical_services || []).filter((s: any) =>
    s.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
    s.display_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
    s.category.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto overflow-y-auto h-[calc(100vh-4rem)]">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-100 flex items-center gap-2.5">
            <Activity className="w-5 h-5 text-blue-400" />
            <span>Windows Subsystems Monitor</span>
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Deep-dive inspection into Windows services, event logs, memory allocators, and network adapters.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={isLoading}
          className="px-4 py-2 rounded-xl bg-surface-elevated hover:bg-gray-700 text-xs font-semibold text-gray-200 border border-surface-border flex items-center gap-2 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-400' : ''}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Tabs Selector */}
      <div className="flex items-center gap-2 border-b border-surface-border pb-3">
        {[
          { id: 'services', label: 'Windows Services', icon: Server, count: servicesData?.critical_services?.length },
          { id: 'events', label: 'Event Logs', icon: FileText, count: eventsData.length },
          { id: 'processes', label: 'Process Activity', icon: Cpu },
          { id: 'network', label: 'Network & DNS', icon: Wifi }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-surface-elevated'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className="text-[10px] bg-gray-800 text-gray-300 px-1.5 py-0.5 rounded-full">
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Services */}
      {activeTab === 'services' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div className="relative max-w-sm w-full">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
              <input
                type="text"
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                placeholder="Search services by name or category..."
                className="w-full bg-surface-elevated border border-surface-border rounded-xl pl-9 pr-4 py-2 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="text-xs text-gray-400">
              Total Windows Services: <strong className="text-gray-200">{servicesData?.total_services || 0}</strong>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredServices.map((s: any, idx: number) => {
              const isRunning = s.status === 'running';
              return (
                <div 
                  key={idx} 
                  className={`p-4 rounded-xl border glass-card space-y-2.5 ${
                    !isRunning ? 'border-amber-700/50 bg-amber-950/20' : 'border-surface-border'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded">
                      {s.category}
                    </span>
                    <span className={`flex items-center gap-1.5 text-xs font-semibold ${
                      isRunning ? 'text-emerald-400' : 'text-amber-400'
                    }`}>
                      <span className={`w-2 h-2 rounded-full ${isRunning ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                      {s.status.toUpperCase()}
                    </span>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-gray-100 truncate">{s.display_name}</h4>
                    <p className="text-xs text-gray-400 font-mono mt-0.5">{s.name}</p>
                  </div>

                  <div className="text-[11px] text-gray-400 pt-1 border-t border-surface-border flex items-center justify-between">
                    <span>Startup: {s.start_type}</span>
                    <span>Expected: Running</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 2: Events */}
      {activeTab === 'events' && (
        <div className="glass-card rounded-2xl border border-surface-border overflow-hidden">
          <div className="p-4 border-b border-surface-border bg-surface-elevated/40 flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-300">Recent Windows Event Log Errors & Warnings (48 hrs)</span>
            <span className="text-xs text-gray-400">{eventsData.length} records retrieved</span>
          </div>

          <div className="divide-y divide-surface-border max-h-[500px] overflow-y-auto">
            {eventsData.length > 0 ? (
              eventsData.map((ev, idx) => (
                <div key={idx} className="p-4 hover:bg-surface-elevated/30 transition-colors space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        ev.level === 'Critical' || ev.level === 'Error'
                          ? 'bg-rose-950/70 text-rose-400 border border-rose-800/60'
                          : 'bg-amber-950/70 text-amber-400 border border-amber-800/60'
                      }`}>
                        {ev.level}
                      </span>
                      <span className="font-semibold text-gray-200">Event ID: {ev.event_id}</span>
                      <span className="text-gray-400">({ev.provider})</span>
                    </div>
                    <span className="text-gray-500 font-mono text-[11px]">{ev.timestamp}</span>
                  </div>
                  <p className="text-xs text-gray-300 font-mono leading-relaxed bg-black/40 p-2 rounded-lg">
                    {ev.message}
                  </p>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-xs text-gray-400">
                No error or warning events logged in the selected window.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Processes */}
      {activeTab === 'processes' && processesData && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top CPU */}
          <div className="glass-card p-5 rounded-2xl border border-surface-border space-y-4">
            <h3 className="text-sm font-bold text-gray-100 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-400" />
              <span>Top CPU Consumers</span>
            </h3>
            <div className="space-y-2">
              {processesData.top_by_cpu.map((p, idx) => (
                <div key={idx} className="p-2.5 rounded-xl bg-surface-elevated/50 border border-surface-border flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-gray-400 text-[10px]">#{idx + 1}</span>
                    <span className="font-semibold text-gray-200">{p.name}</span>
                    {p.is_protected && (
                      <span className="text-[10px] bg-blue-950/70 text-blue-400 px-1.5 py-0.2 rounded border border-blue-800/40">
                        Protected
                      </span>
                    )}
                  </div>
                  <span className="font-bold text-blue-400">{p.cpu_percent}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Top Memory */}
          <div className="glass-card p-5 rounded-2xl border border-surface-border space-y-4">
            <h3 className="text-sm font-bold text-gray-100 flex items-center gap-2">
              <Server className="w-4 h-4 text-purple-400" />
              <span>Top Memory Consumers</span>
            </h3>
            <div className="space-y-2">
              {processesData.top_by_ram.map((p, idx) => (
                <div key={idx} className="p-2.5 rounded-xl bg-surface-elevated/50 border border-surface-border flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-gray-400 text-[10px]">#{idx + 1}</span>
                    <span className="font-semibold text-gray-200">{p.name}</span>
                    {p.is_protected && (
                      <span className="text-[10px] bg-blue-950/70 text-blue-400 px-1.5 py-0.2 rounded border border-blue-800/40">
                        Protected
                      </span>
                    )}
                  </div>
                  <span className="font-bold text-purple-400">{p.memory_mb} MB ({p.memory_percent}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Network */}
      {activeTab === 'network' && networkData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl glass-card border border-surface-border space-y-1">
              <span className="text-xs font-semibold text-gray-400">DNS Resolution</span>
              <p className={`text-lg font-bold flex items-center gap-2 ${networkData.dns_healthy ? 'text-emerald-400' : 'text-rose-400'}`}>
                <span className={`w-2.5 h-2.5 rounded-full ${networkData.dns_healthy ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                {networkData.dns_healthy ? 'Resolved (google.com)' : 'DNS Resolution Failed'}
              </p>
            </div>

            <div className="p-4 rounded-xl glass-card border border-surface-border space-y-1">
              <span className="text-xs font-semibold text-gray-400">Network Traffic (Sent)</span>
              <p className="text-lg font-bold text-white">{networkData.io_summary.bytes_sent_mb} MB</p>
            </div>

            <div className="p-4 rounded-xl glass-card border border-surface-border space-y-1">
              <span className="text-xs font-semibold text-gray-400">Network Traffic (Received)</span>
              <p className="text-lg font-bold text-white">{networkData.io_summary.bytes_recv_mb} MB</p>
            </div>
          </div>

          <div className="glass-card rounded-2xl border border-surface-border overflow-hidden">
            <div className="p-4 border-b border-surface-border bg-surface-elevated/40">
              <h3 className="text-xs font-semibold text-gray-300">Active Network Adapters</h3>
            </div>
            <div className="divide-y divide-surface-border">
              {networkData.interfaces.map((iface, idx) => (
                <div key={idx} className="p-4 flex items-center justify-between text-xs">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-gray-100">{iface.interface}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        iface.is_up ? 'bg-emerald-950/60 text-emerald-400' : 'bg-gray-800 text-gray-400'
                      }`}>
                        {iface.is_up ? 'LINK UP' : 'DOWN'}
                      </span>
                    </div>
                    <p className="text-gray-400 font-mono">
                      IPv4: {iface.ipv4.length > 0 ? iface.ipv4.join(', ') : 'No IPv4 assigned'}
                    </p>
                  </div>
                  <div className="text-right text-gray-400 font-mono">
                    Speed: {iface.speed_mbps ? `${iface.speed_mbps} Mbps` : 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

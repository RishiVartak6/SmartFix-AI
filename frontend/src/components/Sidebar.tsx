import React from 'react';
import { 
  LayoutDashboard, 
  Stethoscope, 
  Activity, 
  Wrench, 
  History, 
  Settings as SettingsIcon, 
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  SlidersHorizontal,
  FlaskConical
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  isAdmin: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, isAdmin }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'diagnose', label: 'Diagnose Problem', icon: Stethoscope, highlight: true },
    { id: 'health', label: 'System Health', icon: Activity },
    { id: 'repairs', label: 'Repair Catalog', icon: Wrench },
    { id: 'history', label: 'Audit & History', icon: History },
    { id: 'demo', label: 'Demo Playground', icon: FlaskConical },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-surface border-r border-surface-border flex flex-col justify-between h-screen select-none">
      <div>
        {/* App Branding */}
        <div className="p-5 border-b border-surface-border flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center shadow-glow">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="font-bold text-lg tracking-tight flex items-center gap-1.5">
              <span>SmartFix</span>
              <span className="text-xs bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded font-mono font-semibold">AI</span>
            </div>
            <p className="text-xs text-gray-400">Windows Diagnostician</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-surface-elevated/70'
                } ${item.highlight && !isActive ? 'hover:border-blue-500/20' : ''}`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-gray-400'}`} />
                <span>{item.label}</span>
                {item.highlight && (
                  <span className="ml-auto flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer / Privilege Badge */}
      <div className="p-4 border-t border-surface-border bg-surface-elevated/30">
        <div className={`flex items-center gap-2.5 p-2.5 rounded-lg text-xs ${
          isAdmin 
            ? 'bg-emerald-950/40 border border-emerald-800/40 text-emerald-400' 
            : 'bg-amber-950/40 border border-amber-800/40 text-amber-400'
        }`}>
          {isAdmin ? (
            <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          ) : (
            <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
          )}
          <div className="truncate">
            <p className="font-semibold">{isAdmin ? 'Administrator Mode' : 'Standard User'}</p>
            <p className="text-[10px] opacity-75">{isAdmin ? 'Full Repair Access' : 'Repairs will prompt UAC'}</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ApprovalModal } from './components/ApprovalModal';
import { ExecutionModal } from './components/ExecutionModal';
import { Dashboard } from './pages/Dashboard';
import { Diagnose } from './pages/Diagnose';
import { SystemHealth as SystemHealthPage } from './pages/SystemHealth';
import { Repairs } from './pages/Repairs';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { DemoPlayground } from './pages/DemoPlayground';

import { api } from './services/api';
import { 
  SystemHealth as SystemHealthType, 
  AppSettingsData, 
  DiagnosisItem, 
  RepairCatalogItem, 
  RepairExecutionResult 
} from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [healthData, setHealthData] = useState<SystemHealthType | null>(null);
  const [settingsData, setSettingsData] = useState<AppSettingsData | null>(null);
  const [repairsCatalog, setRepairsCatalog] = useState<RepairCatalogItem[]>([]);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [diagnoseQuery, setDiagnoseQuery] = useState<string | undefined>(undefined);

  // Modal States
  const [pendingApproval, setPendingApproval] = useState<{
    diagnosis: DiagnosisItem;
    repair: RepairCatalogItem | null;
  } | null>(null);

  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [executionResult, setExecutionResult] = useState<RepairExecutionResult | null>(null);
  const [showExecutionModal, setShowExecutionModal] = useState<boolean>(false);

  // Load telemetry & app settings
  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      const [h, s, r] = await Promise.all([
        api.getHealth(),
        api.getSettings(),
        api.getRepairsCatalog()
      ]);
      setHealthData(h);
      setSettingsData(s);
      setRepairsCatalog(r.catalog);
    } catch (e) {
      console.error('Failed to load telemetry data', e);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refreshData();
    // Auto-refresh telemetry every 30 seconds
    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Request Repair Approval Handler
  const handleRequestRepair = (diagnosis: DiagnosisItem) => {
    if (!diagnosis.recommended_repair_id) return;
    const repairMeta = repairsCatalog.find(r => r.id === diagnosis.recommended_repair_id) || null;
    setPendingApproval({
      diagnosis,
      repair: repairMeta
    });
  };

  // Manual Trigger from Repair Catalog
  const handleExecuteManualRepair = (repair: RepairCatalogItem) => {
    const mockDiagnosis: DiagnosisItem = {
      id: `manual_${repair.id}`,
      problem: `Manual Execution: ${repair.name}`,
      probable_root_cause: repair.description,
      confidence: 1.0,
      confidence_level: 'high',
      severity: 'medium',
      evidence: ['Manual user-initiated maintenance action'],
      recommended_repair_id: repair.id,
      explanation: repair.description
    };
    setPendingApproval({
      diagnosis: mockDiagnosis,
      repair
    });
  };

  // User Approval Confirmed
  const handleApproveRepair = async () => {
    if (!pendingApproval) return;
    const { diagnosis, repair } = pendingApproval;
    const repairId = repair?.id || diagnosis.recommended_repair_id!;
    
    // Close approval modal & open execution progress
    setPendingApproval(null);
    setShowExecutionModal(true);
    setIsExecuting(true);
    setExecutionResult(null);

    try {
      // 1. Record approval
      await api.approveRepair(repairId, diagnosis.id);
      // 2. Execute validated script
      const result = await api.executeRepair(repairId, diagnosis.id);
      setExecutionResult(result);
      // Refresh health stats after fix
      refreshData();
    } catch (err: any) {
      setExecutionResult({
        record_id: 'error',
        repair_id: repairId,
        repair_name: repair?.name || repairId,
        success: false,
        execution_output: '',
        error_message: err?.message || 'Execution error occurred',
        verified: false,
        verification_success: false,
        verification_message: 'Repair execution failed.',
        verification_details: {},
        duration_ms: 0
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleNavigateDiagnose = (query?: string) => {
    setDiagnoseQuery(query);
    setCurrentTab('diagnose');
  };

  return (
    <div className="flex h-screen bg-background text-gray-100 font-sans overflow-hidden">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={(tab) => {
          setDiagnoseQuery(undefined);
          setCurrentTab(tab);
        }}
        isAdmin={settingsData?.is_admin || false}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          currentTab={currentTab}
          settings={settingsData}
          health={healthData}
          onRefresh={refreshData}
          isRefreshing={isRefreshing}
        />

        <main className="flex-1 overflow-hidden relative">
          {currentTab === 'dashboard' && (
            <Dashboard
              health={healthData}
              isLoading={isRefreshing}
              onNavigateDiagnose={handleNavigateDiagnose}
              onNavigateHealth={() => setCurrentTab('health')}
            />
          )}

          {currentTab === 'diagnose' && (
            <Diagnose
              initialQuery={diagnoseQuery}
              onRequestRepair={handleRequestRepair}
            />
          )}

          {currentTab === 'health' && <SystemHealthPage />}

          {currentTab === 'repairs' && (
            <Repairs
              isAdmin={settingsData?.is_admin || false}
              onExecuteManualRepair={handleExecuteManualRepair}
            />
          )}

          {currentTab === 'history' && <History />}

          {currentTab === 'demo' && (
            <DemoPlayground onNavigateDiagnose={handleNavigateDiagnose} />
          )}

          {currentTab === 'settings' && (
            <Settings
              settings={settingsData}
              onSettingsUpdated={refreshData}
            />
          )}
        </main>
      </div>

      {/* Explicit User Approval Safety Gate Modal */}
      {pendingApproval && (
        <ApprovalModal
          diagnosis={pendingApproval.diagnosis}
          repair={pendingApproval.repair}
          isAdmin={settingsData?.is_admin || false}
          onApprove={handleApproveRepair}
          onCancel={() => setPendingApproval(null)}
        />
      )}

      {/* Live Repair Execution & Verification Modal */}
      {showExecutionModal && (
        <ExecutionModal
          result={executionResult}
          isLoading={isExecuting}
          onClose={() => setShowExecutionModal(false)}
          onRediagnose={() => {
            setShowExecutionModal(false);
            handleNavigateDiagnose();
          }}
        />
      )}
    </div>
  );
};

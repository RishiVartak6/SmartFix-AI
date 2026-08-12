import pytest
from backend.collectors.system import collect_system_info
from backend.collectors.services import collect_services
from backend.collectors.processes import collect_processes
from backend.collectors.network import collect_network_info
from backend.collectors.collector_manager import collect_full_diagnostics

def test_system_collector():
    info = collect_system_info()
    assert "os" in info
    assert "cpu" in info
    assert "memory" in info
    assert "disks" in info
    assert info["cpu"]["usage_percent"] >= 0.0
    assert info["memory"]["total_gb"] > 0

def test_services_collector():
    services = collect_services()
    assert "critical_services" in services
    assert "total_services" in services
    assert services["total_services"] > 0
    assert isinstance(services["critical_services"], list)

def test_processes_collector():
    procs = collect_processes(limit=5)
    assert "top_by_cpu" in procs
    assert "top_by_ram" in procs
    assert len(procs["top_by_ram"]) > 0
    assert "name" in procs["top_by_ram"][0]

def test_network_collector():
    net = collect_network_info()
    assert "interfaces" in net
    assert "has_active_adapter" in net
    assert "dns_healthy" in net
    assert isinstance(net["dns_healthy"], bool)

def test_collector_manager_aggregation():
    diagnostics = collect_full_diagnostics()
    assert "health_status" in diagnostics
    assert diagnostics["health_status"] in ["Healthy", "Attention Required", "Critical"]
    assert "system" in diagnostics
    assert "services" in diagnostics

import pytest
from backend.repairs.registry import get_all_repairs, get_repair_by_id, REPAIR_CATALOG
from backend.repairs.executor import execute_repair_workflow
from backend.repairs.verification import verify_dns_resolution

def test_repair_catalog_completeness():
    repairs = get_all_repairs()
    assert len(repairs) >= 10
    
    # Check essential repair IDs exist
    expected_ids = [
        "restart_windows_update", "restart_print_spooler", "restart_audio_service",
        "flush_dns", "reset_winsock", "renew_ip", "restart_explorer", "run_sfc_scan"
    ]
    for rid in expected_ids:
        repair = get_repair_by_id(rid)
        assert repair is not None, f"Repair {rid} not found"
        assert "risk" in repair
        assert "requires_admin" in repair
        assert "verification" in repair

def test_untrusted_repair_execution_rejected():
    # Attempting to execute an arbitrary command / unlisted ID must immediately fail
    result = execute_repair_workflow("arbitrary_malicious_script_id")
    assert result["success"] is False
    assert "Security Violation" in result["error"]
    assert result["verified"] is False

def test_safe_dns_flush_execution():
    # flush_dns is a safe non-destructive operation on Windows
    result = execute_repair_workflow("flush_dns")
    assert "repair_id" in result
    assert result["repair_id"] == "flush_dns"
    assert result["verified"] is True

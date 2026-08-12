import pytest
from backend.diagnosis.rule_engine import evaluate_rules
from backend.diagnosis.schemas import DiagnosisSchema

def test_rule_engine_stopped_update_service():
    mock_diagnostics = {
        "services": {
            "failed_critical_services": [
                {
                    "name": "wuauserv",
                    "display_name": "Windows Update",
                    "status": "stopped",
                    "start_type": "manual",
                    "category": "Update"
                }
            ]
        },
        "network": {"has_active_adapter": True, "dns_healthy": True},
        "system": {"cpu": {"usage_percent": 10}, "memory": {"usage_percent": 40}, "primary_disk_percent": 30},
        "events": [],
        "application_crashes": []
    }
    
    diagnoses = evaluate_rules(mock_diagnostics)
    assert len(diagnoses) >= 1
    update_diag = next((d for d in diagnoses if d.recommended_repair_id == "restart_windows_update"), None)
    assert update_diag is not None
    assert update_diag.confidence >= 0.90
    assert "Windows Update" in update_diag.problem

def test_rule_engine_dns_failure():
    mock_diagnostics = {
        "services": {"failed_critical_services": []},
        "network": {"has_active_adapter": True, "dns_healthy": False},
        "system": {"cpu": {"usage_percent": 10}, "memory": {"usage_percent": 40}, "primary_disk_percent": 30},
        "events": [],
        "application_crashes": []
    }
    diagnoses = evaluate_rules(mock_diagnostics)
    dns_diag = next((d for d in diagnoses if d.recommended_repair_id == "flush_dns"), None)
    assert dns_diag is not None
    assert dns_diag.severity == "high"

def test_rule_engine_user_query_audio():
    mock_diagnostics = {
        "services": {"failed_critical_services": []},
        "network": {"has_active_adapter": True, "dns_healthy": True},
        "system": {"cpu": {"usage_percent": 10}, "memory": {"usage_percent": 40}, "primary_disk_percent": 30},
        "events": [],
        "application_crashes": []
    }
    diagnoses = evaluate_rules(mock_diagnostics, user_query="I have no sound coming from my speakers")
    audio_diag = next((d for d in diagnoses if d.recommended_repair_id == "restart_audio_service"), None)
    assert audio_diag is not None
    assert audio_diag.confidence >= 0.80

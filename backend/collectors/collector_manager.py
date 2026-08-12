import logging
from typing import Dict, Any, Optional
from backend.collectors.system import collect_system_info
from backend.collectors.events import collect_event_logs
from backend.collectors.services import collect_services
from backend.collectors.processes import collect_processes
from backend.collectors.network import collect_network_info
from backend.collectors.application import collect_application_crashes
from backend.collectors.drivers import collect_driver_issues

logger = logging.getLogger("smartfix.collector_manager")

def collect_full_diagnostics(user_query: Optional[str] = None) -> Dict[str, Any]:
    """
    Collects and aggregates structured diagnostic snapshot across all subsystems.
    Preprocesses and summarizes data to ensure high relevance and clarity.
    """
    logger.info("Gathering full system diagnostics...")
    
    system = collect_system_info()
    services = collect_services()
    events = collect_event_logs(hours=24, max_events=20)
    processes = collect_processes(limit=10)
    network = collect_network_info()
    app_crashes = collect_application_crashes(hours=48, max_events=10)
    drivers = collect_driver_issues()

    # Determine quick health indicators
    attention_reasons = []
    if services.get("failed_critical_services"):
        names = [s["display_name"] for s in services["failed_critical_services"]]
        attention_reasons.append(f"Critical Windows service(s) stopped: {', '.join(names)}")
    
    if system["cpu"]["usage_percent"] > 85.0:
        attention_reasons.append(f"High CPU utilization ({system['cpu']['usage_percent']}%)")
        
    if system["memory"]["usage_percent"] > 90.0:
        attention_reasons.append(f"Critical Memory pressure ({system['memory']['usage_percent']}%)")
        
    if not network["dns_healthy"] and network["has_active_adapter"]:
        attention_reasons.append("DNS Resolution failure detected on active network adapter")

    if not network["has_active_adapter"]:
        attention_reasons.append("No active network adapter connected")

    if len(app_crashes) > 0:
        attention_reasons.append(f"{len(app_crashes)} recent application crash/hang event(s) recorded")

    health_status = "Critical" if (len(services.get("failed_critical_services", [])) > 1 or system["cpu"]["usage_percent"] > 90 or system["memory"]["usage_percent"] > 95) else \
                    ("Attention Required" if len(attention_reasons) > 0 else "Healthy")

    return {
        "health_status": health_status,
        "attention_reasons": attention_reasons,
        "system": system,
        "services": services,
        "events": events,
        "processes": processes,
        "network": network,
        "application_crashes": app_crashes,
        "drivers": drivers,
        "user_query": user_query
    }

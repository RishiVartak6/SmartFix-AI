import psutil
import logging
from typing import List, Dict, Any

logger = logging.getLogger("smartfix.services")

# Essential services targeted for diagnosis and recovery
CRITICAL_SERVICES = {
    "wuauserv": {"name": "Windows Update", "category": "Update", "recommended_status": "running"},
    "bits": {"name": "Background Intelligent Transfer Service", "category": "Update", "recommended_status": "running"},
    "Spooler": {"name": "Print Spooler", "category": "Printing", "recommended_status": "running"},
    "AudioSrv": {"name": "Windows Audio", "category": "Audio", "recommended_status": "running"},
    "AudioEndpointBuilder": {"name": "Windows Audio Endpoint Builder", "category": "Audio", "recommended_status": "running"},
    "bthserv": {"name": "Bluetooth Support Service", "category": "Bluetooth", "recommended_status": "running"},
    "W32Time": {"name": "Windows Time", "category": "Time Sync", "recommended_status": "running"},
    "CryptSvc": {"name": "Cryptographic Services", "category": "Security", "recommended_status": "running"},
    "Dhcp": {"name": "DHCP Client", "category": "Network", "recommended_status": "running"},
    "Dnscache": {"name": "DNS Client", "category": "Network", "recommended_status": "running"},
    "Winmgmt": {"name": "Windows Management Instrumentation", "category": "System", "recommended_status": "running"},
    "SysMain": {"name": "SysMain (Superfetch)", "category": "Performance", "recommended_status": "running"}
}

def collect_services() -> Dict[str, Any]:
    """
    Collects Windows services, identifying critical service states and abnormal failures.
    """
    all_services: List[Dict[str, Any]] = []
    critical_status: List[Dict[str, Any]] = []
    failed_services: List[Dict[str, Any]] = []
    
    try:
        for s in psutil.win_service_iter():
            try:
                info = s.as_dict()
                srv_name = info.get("name", "")
                srv_display = info.get("display_name", "")
                srv_status = info.get("status", "unknown")
                srv_start_type = info.get("start_type", "unknown")
                
                service_dict = {
                    "name": srv_name,
                    "display_name": srv_display,
                    "status": srv_status,
                    "start_type": srv_start_type
                }
                
                # Check if critical service
                if srv_name in CRITICAL_SERVICES or srv_name.lower() in CRITICAL_SERVICES:
                    meta = CRITICAL_SERVICES.get(srv_name) or CRITICAL_SERVICES.get(srv_name.lower(), {})
                    crit_dict = {
                        **service_dict,
                        "category": meta.get("category", "General"),
                        "recommended_name": meta.get("name", srv_display),
                        "is_expected_running": meta.get("recommended_status") == "running",
                        "is_degraded": srv_status != "running"
                    }
                    critical_status.append(crit_dict)
                    if srv_status != "running":
                        failed_services.append(crit_dict)
                        
                all_services.append(service_dict)
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Error enumerating Windows services: {e}")

    return {
        "critical_services": critical_status,
        "failed_critical_services": failed_services,
        "total_services": len(all_services),
        "running_count": sum(1 for s in all_services if s.get("status") == "running"),
        "stopped_count": sum(1 for s in all_services if s.get("status") == "stopped")
    }

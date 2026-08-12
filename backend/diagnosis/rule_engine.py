import logging
from typing import Dict, Any, List, Optional
from backend.diagnosis.schemas import DiagnosisSchema
from backend.repairs.registry import REPAIR_CATALOG

logger = logging.getLogger("smartfix.rule_engine")

def evaluate_rules(diagnostics: Dict[str, Any], user_query: Optional[str] = None) -> List[DiagnosisSchema]:
    """
    Deterministic rule-based diagnosis matching known Windows conditions.
    """
    diagnoses: List[DiagnosisSchema] = []
    query_lower = (user_query or "").lower()

    services_data = diagnostics.get("services", {})
    failed_services = services_data.get("failed_critical_services", [])
    network_data = diagnostics.get("network", {})
    system_data = diagnostics.get("system", {})
    events_data = diagnostics.get("events", [])
    app_crashes = diagnostics.get("application_crashes", [])

    # Map failed critical services to known repairs
    for srv in failed_services:
        s_name = srv.get("name", "")
        display = srv.get("display_name") or s_name

        if s_name == "wuauserv" or s_name == "bits":
            diagnoses.append(DiagnosisSchema(
                problem="Windows Update Service is Stopped",
                probable_root_cause=f"The Windows Update background service '{s_name}' is currently in a stopped state, preventing updates and patches from downloading.",
                confidence=0.95,
                severity="medium",
                evidence=[
                    f"Service '{s_name}' status: {srv.get('status')}",
                    f"Startup type: {srv.get('start_type')}",
                    f"Category: {srv.get('category')}"
                ],
                recommended_repair_id="restart_windows_update",
                explanation="The Windows Update service must be running for Windows to verify, download, and install system security updates."
            ))

        elif s_name == "Spooler":
            diagnoses.append(DiagnosisSchema(
                problem="Print Spooler Subsystem is Offline",
                probable_root_cause="The Windows Print Spooler service has halted, disabling printing and local/network printer discovery.",
                confidence=0.96,
                severity="medium",
                evidence=[
                    "Print Spooler (Spooler) service is Stopped",
                    "Printer spooling queue cannot accept jobs"
                ],
                recommended_repair_id="restart_print_spooler",
                explanation="Print Spooler manages all printing jobs sent to your printers. Restarting it clears blocked print pipelines."
            ))

        elif s_name in ["AudioSrv", "AudioEndpointBuilder"]:
            diagnoses.append(DiagnosisSchema(
                problem="Windows Audio Service is Stopped",
                probable_root_cause="The core Windows Audio service or endpoint builder is stopped, causing sound devices to become unresponsive or muted.",
                confidence=0.95,
                severity="high",
                evidence=[
                    f"Service '{s_name}' status: Stopped",
                    "Windows Audio endpoint pipeline is inactive"
                ],
                recommended_repair_id="restart_audio_service",
                explanation="Windows Audio services route sound between applications and your speakers or headphones. Restarting them restores sound devices."
            ))

        elif s_name == "bthserv":
            diagnoses.append(DiagnosisSchema(
                problem="Bluetooth Support Service is Stopped",
                probable_root_cause="Bluetooth service 'bthserv' is not running, which prevents discovery and pairing of Bluetooth peripherals.",
                confidence=0.92,
                severity="low",
                evidence=[
                    "Bluetooth Support Service (bthserv) status: Stopped"
                ],
                recommended_repair_id="restart_bluetooth_service",
                explanation="The Bluetooth Support service discovers and associates remote Bluetooth devices with your PC."
            ))

        elif s_name == "W32Time":
            diagnoses.append(DiagnosisSchema(
                problem="Windows Time Service Inactive",
                probable_root_cause="The Windows Time service is not running, leading to clock drift and SSL/HTTPS certificate validation errors.",
                confidence=0.91,
                severity="medium",
                evidence=[
                    "Service 'W32Time' is Stopped",
                    "Network time synchronization is paused"
                ],
                recommended_repair_id="restart_time_service",
                explanation="Accurate system time is essential for secure web browsing and authentication certificates."
            ))

    # Network / DNS Rules
    if network_data.get("has_active_adapter") and not network_data.get("dns_healthy"):
        diagnoses.append(DiagnosisSchema(
            problem="DNS Name Resolution Failure",
            probable_root_cause="Network adapter is active, but Domain Name System (DNS) queries are failing or returning stale cache responses.",
            confidence=0.92,
            severity="high",
            evidence=[
                "Network interface is UP",
                "DNS query to google.com failed",
                "DNS query to cloudflare.com failed"
            ],
            recommended_repair_id="flush_dns",
            explanation="Flushing the DNS cache purges outdated or corrupt address records and requests fresh DNS addresses."
        ))

    # High RAM Usage Rule
    mem_percent = system_data.get("memory", {}).get("usage_percent", 0.0)
    if mem_percent >= 88.0:
        high_procs = diagnostics.get("processes", {}).get("top_by_ram", [])[:3]
        proc_names = [f"{p['name']} ({p['memory_mb']} MB)" for p in high_procs]
        diagnoses.append(DiagnosisSchema(
            problem="Elevated System Memory Pressure",
            probable_root_cause=f"RAM utilization is at {mem_percent}%. High consumption processes or temporary file caches are saturating physical memory.",
            confidence=0.86,
            severity="medium",
            evidence=[
                f"RAM Utilization: {mem_percent}%",
                f"Top Memory Consumers: {', '.join(proc_names)}"
            ],
            recommended_repair_id="clean_temp_files",
            explanation="Purging obsolete temporary caches frees cached memory resources and unblocks paging."
        ))

    # High CPU Utilization
    cpu_percent = system_data.get("cpu", {}).get("usage_percent", 0.0)
    if cpu_percent >= 90.0:
        high_cpu_procs = diagnostics.get("processes", {}).get("top_by_cpu", [])[:3]
        proc_names = [f"{p['name']} ({p['cpu_percent']}%)" for p in high_cpu_procs]
        diagnoses.append(DiagnosisSchema(
            problem="Severe CPU Saturation",
            probable_root_cause=f"Total CPU usage has surged to {cpu_percent}%, causing system throttling and input lag.",
            confidence=0.88,
            severity="high",
            evidence=[
                f"CPU Utilization: {cpu_percent}%",
                f"Top CPU Processes: {', '.join(proc_names)}"
            ],
            recommended_repair_id="restart_explorer",
            explanation="Restarting hung UI shells or cleaning temp locks helps alleviate hung foreground cycles."
        ))

    # Application Crash Rules
    if app_crashes:
        recent_crash = app_crashes[0]
        diagnoses.append(DiagnosisSchema(
            problem="Application Crash / Error Event Detected",
            probable_root_cause=f"Windows Error Reporting logged an application crash (Event {recent_crash.get('event_id')}): {recent_crash.get('message', '')[:100]}",
            confidence=0.82,
            severity="medium",
            evidence=[
                f"Event ID: {recent_crash.get('event_id')}",
                f"Provider: {recent_crash.get('provider')}",
                f"Timestamp: {recent_crash.get('timestamp')}"
            ],
            recommended_repair_id="run_sfc_scan",
            explanation="Application faults can stem from corrupt Windows shared DLLs or runtime dependencies. Running System File Checker repairs damaged system components."
        ))

    # Natural language query keyword heuristics
    if user_query:
        if any(w in query_lower for w in ["audio", "sound", "volume", "mute", "speaker", "hear"]):
            if not any(d.recommended_repair_id == "restart_audio_service" for d in diagnoses):
                diagnoses.append(DiagnosisSchema(
                    problem="Reported Audio / Sound Output Issue",
                    probable_root_cause="User reported audio failure. Audio endpoint driver or service may be in an invalid state.",
                    confidence=0.80,
                    severity="medium",
                    evidence=[f"User complaint: '{user_query}'"],
                    recommended_repair_id="restart_audio_service",
                    explanation="Restarting the Windows Audio service refreshes audio pipeline endpoints."
                ))
        elif any(w in query_lower for w in ["printer", "print", "spooler", "paper"]):
            if not any(d.recommended_repair_id == "restart_print_spooler" for d in diagnoses):
                diagnoses.append(DiagnosisSchema(
                    problem="Reported Printer / Spooler Issue",
                    probable_root_cause="User reported printer malfunction. Print Spooler queue or service state requires reset.",
                    confidence=0.82,
                    severity="medium",
                    evidence=[f"User complaint: '{user_query}'"],
                    recommended_repair_id="restart_print_spooler",
                    explanation="Restarting the print spooler clears locked print jobs."
                ))
        elif any(w in query_lower for w in ["internet", "dns", "website", "wifi", "network", "connect", "browser"]):
            if not any(d.recommended_repair_id in ["flush_dns", "renew_ip", "reset_winsock"] for d in diagnoses):
                diagnoses.append(DiagnosisSchema(
                    problem="Reported Network Connectivity / DNS Failure",
                    probable_root_cause="User reported internet or browsing trouble. DNS resolver or IP lease requires refresh.",
                    confidence=0.83,
                    severity="medium",
                    evidence=[f"User complaint: '{user_query}'"],
                    recommended_repair_id="flush_dns",
                    explanation="Flushing the DNS cache resolves obsolete IP mappings and restores web browsing."
                ))
        elif any(w in query_lower for w in ["corrupt", "blue screen", "crash", "freeze", "sfc", "dism", "system file"]):
            diagnoses.append(DiagnosisSchema(
                problem="Suspected Windows System Integrity Issue",
                probable_root_cause="System crashes or corrupted core components detected. System File Checker scan is advised.",
                confidence=0.85,
                severity="high",
                evidence=[f"User complaint: '{user_query}'"],
                recommended_repair_id="run_sfc_scan",
                explanation="Running SFC scan will inspect and repair damaged Windows core binaries."
            ))

    return diagnoses

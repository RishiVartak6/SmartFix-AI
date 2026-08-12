from fastapi import APIRouter, Query
from typing import Optional
from backend.collectors.system import collect_system_info
from backend.collectors.events import collect_event_logs
from backend.collectors.services import collect_services
from backend.collectors.processes import collect_processes
from backend.collectors.network import collect_network_info
from backend.collectors.collector_manager import collect_full_diagnostics

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/health")
async def get_system_health():
    """Returns real-time system health summary and key alert indicators."""
    diagnostics = collect_full_diagnostics()
    return {
        "health_status": diagnostics["health_status"],
        "attention_reasons": diagnostics["attention_reasons"],
        "cpu_percent": diagnostics["system"]["cpu"]["usage_percent"],
        "memory_percent": diagnostics["system"]["memory"]["usage_percent"],
        "disk_percent": diagnostics["system"]["primary_disk_percent"],
        "network_status": diagnostics["network"]["status"],
        "dns_healthy": diagnostics["network"]["dns_healthy"],
        "failed_services_count": len(diagnostics["services"]["failed_critical_services"]),
        "failed_critical_services": diagnostics["services"]["failed_critical_services"],
        "total_services": diagnostics["services"]["total_services"],
        "recent_event_errors": len(diagnostics["events"]),
        "uptime_hours": diagnostics["system"]["os"]["uptime_hours"]
    }

@router.get("/info")
async def get_system_info():
    """Returns comprehensive OS and hardware metrics."""
    return collect_system_info()

@router.get("/events")
async def get_events(
    hours: int = Query(24, ge=1, le=168),
    max_events: int = Query(30, ge=1, le=100)
):
    """Returns filtered Windows Event Logs."""
    return collect_event_logs(hours=hours, max_events=max_events)

@router.get("/services")
async def get_services():
    """Returns Windows services list and health state."""
    return collect_services()

@router.get("/processes")
async def get_processes(limit: int = Query(15, ge=5, le=50)):
    """Returns top resource consuming processes."""
    return collect_processes(limit=limit)

@router.get("/network")
async def get_network():
    """Returns network adapter details and connectivity checks."""
    return collect_network_info()

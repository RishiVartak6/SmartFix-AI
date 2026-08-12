import psutil
import logging
from typing import List, Dict, Any

logger = logging.getLogger("smartfix.processes")

CRITICAL_SYSTEM_PROCESSES = {
    "system", "system idle process", "csrss.exe", "smss.exe", "wininit.exe", 
    "services.exe", "lsass.exe", "svchost.exe", "explorer.exe", "smartfix.exe", "python.exe"
}

def collect_processes(limit: int = 15) -> Dict[str, Any]:
    """
    Collects top resource-consuming processes, detecting CPU or Memory spikes.
    """
    proc_list: List[Dict[str, Any]] = []
    high_cpu_procs: List[Dict[str, Any]] = []
    high_ram_procs: List[Dict[str, Any]] = []

    try:
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
            try:
                p_info = p.info
                name = p_info.get('name') or "Unknown"
                cpu_p = p_info.get('cpu_percent') or 0.0
                mem_p = round(p_info.get('memory_percent') or 0.0, 2)
                mem_bytes = p_info.get('memory_info').rss if p_info.get('memory_info') else 0
                mem_mb = round(mem_bytes / (1024 * 1024), 1)
                
                is_system = name.lower() in CRITICAL_SYSTEM_PROCESSES

                item = {
                    "pid": p_info.get('pid'),
                    "name": name,
                    "cpu_percent": cpu_p,
                    "memory_percent": mem_p,
                    "memory_mb": mem_mb,
                    "is_protected": is_system
                }
                
                proc_list.append(item)
                
                if cpu_p >= 25.0 and not is_system:
                    high_cpu_procs.append(item)
                if mem_p >= 15.0 and not is_system:
                    high_ram_procs.append(item)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logger.error(f"Error enumerating processes: {e}")

    # Sort by CPU usage and RAM usage
    sorted_by_cpu = sorted(proc_list, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    sorted_by_ram = sorted(proc_list, key=lambda x: x['memory_mb'], reverse=True)[:limit]

    return {
        "top_by_cpu": sorted_by_cpu,
        "top_by_ram": sorted_by_ram,
        "high_cpu_anomalies": high_cpu_procs,
        "high_ram_anomalies": high_ram_procs,
        "total_active_processes": len(proc_list)
    }

import psutil
import socket
import subprocess
import logging
from typing import Dict, Any, List

logger = logging.getLogger("smartfix.network")

def check_dns_resolution(host: str = "google.com", timeout: float = 2.0) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname(host)
        return True
    except Exception:
        return False

def collect_network_info() -> Dict[str, Any]:
    """
    Collects network adapter status, DNS health, and connection metrics.
    """
    interfaces = []
    has_active_adapter = False
    
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for name, addr_list in addrs.items():
            stat = stats.get(name)
            is_up = stat.isup if stat else False
            speed = stat.speed if stat else 0
            
            ipv4_list = [a.address for a in addr_list if a.family == socket.AF_INET]
            if is_up and ipv4_list and not ipv4_list[0].startswith("127."):
                has_active_adapter = True

            interfaces.append({
                "interface": name,
                "is_up": is_up,
                "speed_mbps": speed,
                "ipv4": ipv4_list,
                "is_loopback": any(a.startswith("127.") for a in ipv4_list)
            })
    except Exception as e:
        logger.error(f"Error inspecting network interfaces: {e}")

    # DNS checks
    dns_google = check_dns_resolution("google.com", timeout=2.0)
    dns_cloudflare = check_dns_resolution("cloudflare.com", timeout=2.0)
    dns_healthy = dns_google or dns_cloudflare

    # Check network IO counters
    try:
        io_counters = psutil.net_io_counters()
        io_summary = {
            "bytes_sent_mb": round(io_counters.bytes_sent / (1024 * 1024), 2),
            "bytes_recv_mb": round(io_counters.bytes_recv / (1024 * 1024), 2),
            "errin": io_counters.errin,
            "errout": io_counters.errout
        }
    except Exception:
        io_summary = {"bytes_sent_mb": 0, "bytes_recv_mb": 0, "errin": 0, "errout": 0}

    return {
        "interfaces": interfaces,
        "has_active_adapter": has_active_adapter,
        "dns_healthy": dns_healthy,
        "dns_google_ok": dns_google,
        "dns_cloudflare_ok": dns_cloudflare,
        "io_summary": io_summary,
        "status": "connected" if (has_active_adapter and dns_healthy) else ("dns_issue" if has_active_adapter else "disconnected")
    }

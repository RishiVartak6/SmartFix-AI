import subprocess
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("smartfix.drivers")

def collect_driver_issues() -> List[Dict[str, Any]]:
    """
    Checks for device driver error states using PnP entity queries.
    """
    ps_script = """
    try {
        $problemDevices = Get-PnpDevice -Status "Error", "Degraded", "Unknown" -ErrorAction SilentlyContinue | Select-Object -First 10
        if ($problemDevices) {
            $problemDevices | Select-Object FriendlyName, InstanceId, Status, Class | ConvertTo-Json -Compress
        } else {
            "[]"
        }
    } catch {
        "[]"
    }
    """
    try:
        startupinfo = None
        if hasattr(subprocess, 'STARTUPINFO'):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 6

        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=8,
            startupinfo=startupinfo
        )
        out = proc.stdout.strip()
        if out:
            data = json.loads(out)
            return [data] if isinstance(data, dict) else data
    except Exception as e:
        logger.error(f"Error checking driver status: {e}")
        
    return []

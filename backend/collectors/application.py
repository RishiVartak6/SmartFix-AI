import subprocess
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("smartfix.application")

def collect_application_crashes(hours: int = 48, max_events: int = 15) -> List[Dict[str, Any]]:
    """
    Collects application crash events (Event ID 1000 - Application Error, 1002 - Application Hang, 1001 - WER).
    """
    ps_script = f"""
    $startTime = (Get-Date).AddHours(-{hours})
    $filter = @{{
        LogName = 'Application'
        Id = @(1000, 1001, 1002)
        StartTime = $startTime
    }}
    
    try {{
        $events = Get-WinEvent -FilterHashtable $filter -MaxEvents {max_events} -ErrorAction SilentlyContinue
        if ($events) {{
            $result = @()
            foreach ($e in $events) {{
                $type = switch ($e.Id) {{
                    1000 {{ "Crash (Application Error)" }}
                    1001 {{ "Windows Error Report (WER)" }}
                    1002 {{ "Application Hang" }}
                    default {{ "Application Event" }}
                }}
                
                $msg = $e.Message
                if ($msg -and $msg.Length -gt 250) {{
                    $msg = $msg.Substring(0, 247) + "..."
                }}
                
                $result += [PSCustomObject]@{{
                    event_id = $e.Id
                    type = $type
                    timestamp = $e.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss")
                    provider = $e.ProviderName
                    message = if ($msg) {{ $msg }} else {{ "Application error occurred" }}
                }}
            }}
            $result | ConvertTo-Json -Compress
        }} else {{
            "[]"
        }}
    }} catch {{
        "[]"
    }}
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
        logger.error(f"Error collecting application crashes: {e}")
        
    return []

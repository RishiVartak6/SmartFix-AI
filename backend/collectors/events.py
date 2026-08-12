import subprocess
import json
import datetime
import logging
from typing import List, Dict, Any

logger = logging.getLogger("smartfix.events")

def collect_event_logs(hours: int = 24, max_events: int = 40) -> List[Dict[str, Any]]:
    """
    Collects Error, Critical, and Warning events from System and Application logs.
    Uses PowerShell Get-WinEvent with JSON output for robust, structured parsing.
    """
    events: List[Dict[str, Any]] = []
    
    # PowerShell script to retrieve top recent Error (2), Critical (1), and Warning (3) events
    ps_script = f"""
    $startTime = (Get-Date).AddHours(-{hours})
    $filter = @{{
        LogName = @('System', 'Application')
        Level = @(1, 2, 3)
        StartTime = $startTime
    }}
    
    try {{
        $rawEvents = Get-WinEvent -FilterHashtable $filter -MaxEvents {max_events} -ErrorAction SilentlyContinue
        if ($rawEvents) {{
            $result = @()
            foreach ($e in $rawEvents) {{
                $levelStr = switch ($e.Level) {{
                    1 {{ "Critical" }}
                    2 {{ "Error" }}
                    3 {{ "Warning" }}
                    default {{ "Information" }}
                }}
                
                $msg = $e.Message
                if ($msg -and $msg.Length -gt 250) {{
                    $msg = $msg.Substring(0, 247) + "..."
                }}
                
                $result += [PSCustomObject]@{{
                    event_id = $e.Id
                    provider = $e.ProviderName
                    log_name = $e.LogName
                    level = $levelStr
                    timestamp = $e.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss")
                    message = if ($msg) {{ $msg }} else {{ "No message provided" }}
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
            startupinfo.wShowWindow = 6 # SW_MINIMIZE / SW_HIDE

        process = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=8,
            startupinfo=startupinfo
        )
        
        output = process.stdout.strip()
        if output:
            try:
                parsed = json.loads(output)
                if isinstance(parsed, dict):
                    events.append(parsed)
                elif isinstance(parsed, list):
                    events.extend(parsed)
            except json.JSONDecodeError:
                logger.warning("Failed to decode JSON from Get-WinEvent")
    except Exception as e:
        logger.error(f"Error querying Windows Event Logs: {e}")

    return events

"""
SmartFix AI — System Health Report Generator
Generates a full HTML report of system health, diagnostics, and repair history.
"""
import subprocess
import os
import sys
import platform
import time
import socket
from datetime import datetime
from typing import Dict, Any

def _ps(script: str, timeout: int = 30) -> str:
    try:
        r = subprocess.run(
            ["powershell", "-NonInteractive", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True, text=True, timeout=timeout
        )
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return str(e)

def collect_system_info() -> dict:
    info = {}
    
    info["hostname"]  = socket.gethostname()
    info["os"]        = platform.platform()
    info["python"]    = sys.version.split()[0]
    info["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info["uptime"]    = _ps("(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime | Select-Object -ExpandProperty TotalHours | ForEach-Object { [Math]::Round($_, 1) }")

    
    info["cpu"]       = _ps("(Get-WmiObject Win32_Processor).Name")
    info["cpu_cores"] = _ps("(Get-WmiObject Win32_Processor).NumberOfCores")
    info["ram_gb"]    = _ps("[Math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)")
    info["gpu"]       = _ps("(Get-WmiObject Win32_VideoController | Where-Object { $_.Name -notlike '*Basic*' } | Select-Object -First 1).Name")
    info["mobo"]      = _ps("(Get-WmiObject Win32_BaseBoard).Product")

    
    info["windows_ver"]    = _ps("(Get-WmiObject Win32_OperatingSystem).Caption")
    info["windows_build"]  = _ps("(Get-WmiObject Win32_OperatingSystem).BuildNumber")
    info["activation"]     = _ps("(Get-WmiObject SoftwareLicensingProduct | Where-Object { $_.Name -like 'Windows*' -and $_.LicenseStatus -eq 1 }).LicenseStatus")
    info["last_update"]    = _ps("(Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1).InstalledOn")

    
    info["cpu_usage"]   = _ps("(Get-WmiObject Win32_Processor).LoadPercentage")
    info["ram_used"]    = _ps("$os = Get-WmiObject Win32_OperatingSystem; [Math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 1)")
    info["ram_free"]    = _ps("$os = Get-WmiObject Win32_OperatingSystem; [Math]::Round($os.FreePhysicalMemory / 1MB, 1)")
    info["disk_c"]      = _ps("$d = Get-PSDrive C; \"Used: $([Math]::Round($d.Used/1GB,1)) GB | Free: $([Math]::Round($d.Free/1GB,1)) GB | Total: $([Math]::Round(($d.Used+$d.Free)/1GB,1)) GB\"")
    info["disk_pct"]    = _ps("$d = Get-PSDrive C; [Math]::Round($d.Used/($d.Used+$d.Free)*100, 1)")

    
    info["critical_services"] = _ps("""
$services = @('wuauserv','WinDefend','Spooler','AudioSrv','Dnscache','Dhcp','MpsSvc','EventLog','CryptSvc','winmgmt')
$results = $services | ForEach-Object {
    $s = Get-Service $_ -ErrorAction SilentlyContinue
    if ($s) { "$_|$($s.Status)" }
}
$results -join ';'
""")

    
    info["defender_enabled"] = _ps("(Get-MpComputerStatus -ErrorAction SilentlyContinue).RealTimeProtectionEnabled")
    info["firewall"]         = _ps("(Get-NetFirewallProfile -Profile Domain,Public,Private -ErrorAction SilentlyContinue | Where-Object Enabled -eq True).Count")
    info["tpm"]              = _ps("(Get-Tpm -ErrorAction SilentlyContinue).TpmPresent")
    info["secure_boot"]      = _ps("Confirm-SecureBootUEFI -ErrorAction SilentlyContinue")

    
    info["recent_errors"] = _ps("""
$since = (Get-Date).AddHours(-24)
$count = (Get-WinEvent -LogName System -ErrorAction SilentlyContinue | Where-Object { $_.Level -le 2 -and $_.TimeCreated -gt $since }).Count
Write-Output $count
""")

    
    info["startup_count"] = _ps("(Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue).Count")

    
    info["ip_address"]   = _ps("(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -ne 'WellKnown' } | Select-Object -First 1).IPAddress")
    info["dns_servers"]  = _ps("(Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object { $_.ServerAddresses } | Select-Object -First 1).ServerAddresses -join ', '")
    info["adapter"]      = _ps("(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).Name")

    return info

def generate_html_report(history_records: list = None) -> str:
    info = collect_system_info()
    ts = info.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cpu_pct = info.get("cpu_usage", "—")
    disk_pct = float(info.get("disk_pct", 0) or 0)

    def status_badge(ok: bool) -> str:
        color = "#00D26A" if ok else "#FF3A3A"
        text  = "✓ OK" if ok else "✗ FAILED"
        return f'<span style="background:{color};color:white;padding:2px 10px;border-radius:4px;font-size:12px;font-weight:bold">{text}</span>'

    def progress_bar(val: float, warn: float = 70, crit: float = 90) -> str:
        color = "#FF3A3A" if val >= crit else "#FF8C00" if val >= warn else "#00D26A"
        return f'''<div style="background:#30363D;border-radius:4px;height:8px;width:100%">
            <div style="background:{color};width:{min(val,100):.0f}%;height:8px;border-radius:4px"></div></div>
            <small style="color:#8B949E">{val:.1f}%</small>'''

    
    service_rows = ""
    svc_raw = info.get("critical_services", "")
    for pair in svc_raw.split(";"):
        if "|" in pair:
            name, status = pair.split("|", 1)
            color = "#00D26A" if status.strip().lower() == "running" else "#FF3A3A"
            service_rows += f'''<tr><td>{name}</td>
                <td><span style="color:{color};font-weight:bold">{status}</span></td></tr>'''

    
    history_html = ""
    if history_records:
        for r in history_records[:20]:
            action_color = {"REPAIRED": "#00D26A", "DETECTED": "#FF8C00", "IGNORED": "#8B949E"}.get(r.get("action", ""), "#fff")
            succ = ""
            if r.get("action") == "REPAIRED":
                succ = "✓" if r.get("success") else "✗"
            ts_short = str(r.get("timestamp", ""))[:16]
            history_html += f'''<tr>
                <td>{ts_short}</td>
                <td>{r.get("error_name","")}</td>
                <td>{r.get("category","")}</td>
                <td style="color:{action_color};font-weight:bold">{r.get("action","")} {succ}</td>
            </tr>'''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SmartFix AI — System Health Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0D1117; color: #F0F6FC; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 30px 24px; }}
  .header {{ background: linear-gradient(135deg, #161B22 0%, #0D1117 100%); border: 1px solid #30363D;
             border-radius: 12px; padding: 28px 32px; margin-bottom: 24px; display: flex; align-items: center; gap: 20px; }}
  .header h1 {{ font-size: 26px; color: #4F8EF7; }}
  .header p {{ color: #8B949E; font-size: 13px; margin-top: 4px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 24px; }}
  .card {{ background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 20px 24px; }}
  .card h2 {{ color: #4F8EF7; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;
               border-bottom: 1px solid #30363D; padding-bottom: 8px; }}
  .row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #21262D; }}
  .row .label {{ color: #8B949E; font-size: 12px; }}
  .row .value {{ color: #F0F6FC; font-weight: 500; font-size: 12px; max-width: 55%; text-align: right; word-break: break-word; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ color: #8B949E; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
        padding: 8px 12px; text-align: left; border-bottom: 1px solid #30363D; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #21262D; font-size: 12px; color: #F0F6FC; }}
  tr:last-child td {{ border: none; }}
  .badge-ok {{ background: #00D26A20; color: #00D26A; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
  .badge-warn {{ background: #FF8C0020; color: #FF8C00; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
  .badge-crit {{ background: #FF3A3A20; color: #FF3A3A; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
  .footer {{ text-align: center; color: #6E7681; font-size: 11px; margin-top: 30px; padding-top: 16px; border-top: 1px solid #21262D; }}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <div style="font-size:48px">🛡</div>
    <div>
      <h1>SmartFix AI — System Health Report</h1>
      <p>Generated: {ts} &nbsp;|&nbsp; Host: {info.get("hostname","—")} &nbsp;|&nbsp; OS: {info.get("windows_ver","—")}</p>
    </div>
  </div>

  <div class="grid">

    <!-- System Info -->
    <div class="card">
      <h2>⚙️ System Information</h2>
      <div class="row"><span class="label">CPU</span><span class="value">{info.get("cpu","—")}</span></div>
      <div class="row"><span class="label">CPU Cores</span><span class="value">{info.get("cpu_cores","—")}</span></div>
      <div class="row"><span class="label">RAM</span><span class="value">{info.get("ram_gb","—")} GB</span></div>
      <div class="row"><span class="label">GPU</span><span class="value">{info.get("gpu","—")}</span></div>
      <div class="row"><span class="label">Motherboard</span><span class="value">{info.get("mobo","—")}</span></div>
      <div class="row"><span class="label">Windows</span><span class="value">{info.get("windows_ver","—")}</span></div>
      <div class="row"><span class="label">Build</span><span class="value">{info.get("windows_build","—")}</span></div>
      <div class="row"><span class="label">Last Update</span><span class="value">{info.get("last_update","—")}</span></div>
      <div class="row"><span class="label">Uptime</span><span class="value">{info.get("uptime","—")} hours</span></div>
    </div>

    <!-- Performance -->
    <div class="card">
      <h2>📊 Performance</h2>
      <div class="row"><span class="label">CPU Usage</span><span class="value">{cpu_pct}%</span></div>
      <div style="margin:4px 0 12px">{progress_bar(float(cpu_pct or 0))}</div>
      <div class="row"><span class="label">RAM Used</span><span class="value">{info.get("ram_used","—")} GB</span></div>
      <div style="margin:4px 0 12px">{progress_bar(float(str(info.get("ram_pct","0")).replace("%","") or 0))}</div>
      <div class="row"><span class="label">Disk C:</span><span class="value">{info.get("disk_c","—")}</span></div>
      <div style="margin:4px 0 12px">{progress_bar(disk_pct)}</div>
      <div class="row"><span class="label">Startup Items</span><span class="value">{info.get("startup_count","—")}</span></div>
      <div class="row"><span class="label">Recent Errors (24h)</span>
        <span class="value">
          {"<span class='badge-crit'>" + str(info.get("recent_errors","0")) + " errors</span>" if int(info.get("recent_errors","0") or 0) > 0 else "<span class='badge-ok'>0 errors</span>"}
        </span>
      </div>
    </div>

    <!-- Security -->
    <div class="card">
      <h2>🔒 Security Status</h2>
      <div class="row"><span class="label">Windows Defender</span>
        <span class="value">{"<span class='badge-ok'>ENABLED</span>" if str(info.get("defender_enabled","")).lower() == "true" else "<span class='badge-crit'>DISABLED</span>"}</span>
      </div>
      <div class="row"><span class="label">Firewall Profiles</span>
        <span class="value">{"<span class='badge-ok'>Active</span>" if int(info.get("firewall","0") or 0) > 0 else "<span class='badge-crit'>OFF</span>"}</span>
      </div>
      <div class="row"><span class="label">TPM 2.0</span>
        <span class="value">{"<span class='badge-ok'>Present</span>" if str(info.get("tpm","")).lower() == "true" else "<span class='badge-warn'>Not Found</span>"}</span>
      </div>
      <div class="row"><span class="label">Secure Boot</span>
        <span class="value">{"<span class='badge-ok'>Enabled</span>" if str(info.get("secure_boot","")).lower() == "true" else "<span class='badge-warn'>Disabled</span>"}</span>
      </div>
      <div class="row"><span class="label">Windows Activation</span>
        <span class="value">{"<span class='badge-ok'>Activated</span>" if info.get("activation") == "1" else "<span class='badge-warn'>Check Needed</span>"}</span>
      </div>
    </div>

    <!-- Network -->
    <div class="card">
      <h2>🌐 Network</h2>
      <div class="row"><span class="label">Adapter</span><span class="value">{info.get("adapter","—")}</span></div>
      <div class="row"><span class="label">IP Address</span><span class="value">{info.get("ip_address","—")}</span></div>
      <div class="row"><span class="label">DNS Servers</span><span class="value">{info.get("dns_servers","—")}</span></div>
    </div>

  </div>

  <!-- Services Table -->
  <div class="card" style="margin-bottom:24px">
    <h2>⚙️ Critical Services Status</h2>
    <table>
      <tr><th>Service</th><th>Status</th></tr>
      {service_rows if service_rows else "<tr><td colspan='2' style='color:#8B949E'>Could not retrieve services</td></tr>"}
    </table>
  </div>

  <!-- Repair History -->
  {"<div class='card'><h2>📋 Recent Repair History</h2><table><tr><th>Time</th><th>Error</th><th>Category</th><th>Action</th></tr>" + history_html + "</table></div>" if history_html else ""}

  <div class="footer">
    SmartFix AI — B.E. Computer Engineering Major Project &nbsp;|&nbsp; Report generated {ts}
  </div>

</div>
</body>
</html>"""
    return html

def save_report(output_path: str = None, history_records: list = None) -> str:
    if output_path is None:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(desktop, f"SmartFix_Report_{ts}.html")
    html = generate_html_report(history_records)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path

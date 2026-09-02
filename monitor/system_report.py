"""
SmartFix AI — System Health Report Generator
All data collected in ONE batched PowerShell call (no popup spam).
Pure psutil used for live CPU/RAM/Disk (accurate and instant).
"""
import subprocess
import os
import sys
import platform
import socket
import psutil
from datetime import datetime
from typing import Dict, Any


CREATE_NO_WINDOW = 0x08000000


def _ps_batch(script: str, timeout: int = 45) -> str:
    """Run a single PowerShell script with NO visible window."""
    try:
        r = subprocess.run(
            ["powershell", "-NonInteractive", "-NoProfile",
             "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True, text=True, timeout=timeout,
            creationflags=CREATE_NO_WINDOW
        )
        return (r.stdout or "").strip()
    except Exception as e:
        return str(e)


_BATCH_SCRIPT = r"""
$out = @{}
try { $out['hostname']       = $env:COMPUTERNAME } catch {}
try { $out['os']             = (Get-WmiObject Win32_OperatingSystem).Caption } catch {}
try { $out['build']          = (Get-WmiObject Win32_OperatingSystem).BuildNumber } catch {}
try { $out['cpu']            = (Get-WmiObject Win32_Processor | Select-Object -First 1).Name } catch {}
try { $out['cpu_cores']      = (Get-WmiObject Win32_Processor | Select-Object -First 1).NumberOfCores } catch {}
try { $out['ram_gb']         = [Math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1) } catch {}
try { $out['gpu']            = (Get-WmiObject Win32_VideoController | Where-Object { $_.Name -notlike '*Basic*' } | Select-Object -First 1).Name } catch {}
try { $out['mobo']           = (Get-WmiObject Win32_BaseBoard).Product } catch {}
try { $out['uptime']         = [Math]::Round(((Get-Date) - (Get-WmiObject Win32_OperatingSystem).ConvertToDateTime((Get-WmiObject Win32_OperatingSystem).LastBootUpTime)).TotalHours, 1) } catch {}
try { $out['last_update']    = (Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1).InstalledOn } catch {}
try { $d = Get-PSDrive C; $out['disk_used'] = [Math]::Round($d.Used/1GB,1); $out['disk_free'] = [Math]::Round($d.Free/1GB,1); $out['disk_total'] = [Math]::Round(($d.Used+$d.Free)/1GB,1); $out['disk_pct'] = [Math]::Round($d.Used/($d.Used+$d.Free)*100,1) } catch {}
try { $out['ip']             = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -ne 'WellKnown' } | Select-Object -First 1).IPAddress } catch {}
try { $out['dns']            = ((Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object { $_.ServerAddresses } | Select-Object -First 1).ServerAddresses) -join ', ' } catch {}
try { $out['adapter']        = (Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).Name } catch {}
try { $out['defender']       = (Get-MpComputerStatus -ErrorAction SilentlyContinue).RealTimeProtectionEnabled } catch {}
try { $out['firewall']       = (Get-NetFirewallProfile -Profile Domain,Public,Private -ErrorAction SilentlyContinue | Where-Object Enabled -eq True).Count } catch {}
try { $out['tpm']            = (Get-Tpm -ErrorAction SilentlyContinue).TpmPresent } catch {}
try { $out['secureboot']     = Confirm-SecureBootUEFI -ErrorAction SilentlyContinue } catch { $out['secureboot'] = 'Unknown' }
try { $out['activation']     = (Get-WmiObject SoftwareLicensingProduct | Where-Object { $_.Name -like 'Windows*' -and $_.LicenseStatus -eq 1 } | Select-Object -First 1).LicenseStatus } catch {}
try { $out['startup_count']  = (Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue).Count } catch {}
try {
    $since = (Get-Date).AddHours(-24)
    $out['recent_errors'] = (Get-WinEvent -LogName System -ErrorAction SilentlyContinue | Where-Object { $_.Level -le 2 -and $_.TimeCreated -gt $since }).Count
} catch { $out['recent_errors'] = 0 }
try {
    $svcs = @('wuauserv','WinDefend','Spooler','AudioSrv','Dnscache','Dhcp','MpsSvc','EventLog','CryptSvc','winmgmt')
    $out['services'] = ($svcs | ForEach-Object {
        $s = Get-Service $_ -ErrorAction SilentlyContinue
        if ($s) { "$_|$($s.Status)" }
    }) -join ';'
} catch {}

$out.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }
"""


def collect_system_info() -> dict:
    """Collect all system info in ONE PowerShell call + psutil for live metrics."""
    info = {}
    info["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info["python"] = sys.version.split()[0]

    # Live metrics via psutil (instant, no subprocess)
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        info["cpu_usage"]  = f"{cpu:.1f}"
        info["ram_used"]   = f"{mem.used / (1024**3):.1f}"
        info["ram_free"]   = f"{mem.available / (1024**3):.1f}"
        info["ram_pct"]    = f"{mem.percent:.1f}"
        info["disk_pct"]   = f"{disk.percent:.1f}"
        info["disk_used"]  = f"{disk.used / (1024**3):.1f}"
        info["disk_free"]  = f"{disk.free / (1024**3):.1f}"
        info["disk_total"] = f"{disk.total / (1024**3):.1f}"
    except Exception:
        pass

    # One batched PowerShell call for everything else
    raw = _ps_batch(_BATCH_SCRIPT, timeout=40)
    for line in raw.splitlines():
        if "=" in line:
            key, _, val = line.partition("=")
            info[key.strip()] = val.strip()

    # Derived composite fields
    info["disk_c"] = (
        f"Used: {info.get('disk_used','?')} GB | "
        f"Free: {info.get('disk_free','?')} GB | "
        f"Total: {info.get('disk_total','?')} GB"
    )
    info["windows_ver"]   = info.get("os", platform.platform())
    info["windows_build"] = info.get("build", "—")
    info["critical_services"] = info.get("services", "")

    try:
        info["hostname"] = socket.gethostname()
    except Exception:
        pass

    return info


def generate_html_report(history_records: list = None) -> str:
    info = collect_system_info()
    ts       = info.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cpu_pct  = float(info.get("cpu_usage", 0) or 0)
    disk_pct = float(info.get("disk_pct",  0) or 0)
    ram_pct  = float(info.get("ram_pct",   0) or 0)

    def progress_bar(val: float, warn: float = 70, crit: float = 90) -> str:
        color = "#FF3A3A" if val >= crit else "#FF8C00" if val >= warn else "#00D26A"
        return (
            f'<div style="background:#30363D;border-radius:4px;height:8px;width:100%">'
            f'<div style="background:{color};width:{min(val,100):.0f}%;height:8px;border-radius:4px"></div></div>'
            f'<small style="color:#8B949E">{val:.1f}%</small>'
        )

    def badge(ok: bool, ok_text="OK", fail_text="FAILED") -> str:
        c, t = ("#00D26A", ok_text) if ok else ("#FF3A3A", fail_text)
        return f'<span style="background:{c}20;color:{c};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:bold">{t}</span>'

    # Services table
    service_rows = ""
    for pair in info.get("critical_services", "").split(";"):
        if "|" in pair:
            name, status = pair.split("|", 1)
            c = "#00D26A" if status.strip().lower() == "running" else "#FF3A3A"
            service_rows += (
                f'<tr><td>{name}</td>'
                f'<td><span style="color:{c};font-weight:bold">{status.strip()}</span></td></tr>'
            )

    # History table
    history_html = ""
    if history_records:
        for r in history_records[:20]:
            ac = r.get("action", "")
            ac_color = {"REPAIRED": "#00D26A", "DETECTED": "#FF8C00", "IGNORED": "#8B949E"}.get(ac, "#fff")
            succ = ("✓" if r.get("success") else "✗") if ac == "REPAIRED" else ""
            ts_short = str(r.get("timestamp", ""))[:16]
            history_html += (
                f'<tr><td>{ts_short}</td><td>{r.get("error_name","")}</td>'
                f'<td>{r.get("category","")}</td>'
                f'<td style="color:{ac_color};font-weight:bold">{ac} {succ}</td></tr>'
            )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SmartFix AI — System Health Report</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0D1117;color:#F0F6FC;font-family:'Segoe UI',Arial,sans-serif;font-size:14px}}
  .container{{max-width:1100px;margin:0 auto;padding:30px 24px}}
  .header{{background:linear-gradient(135deg,#161B22 0%,#0D1117 100%);border:1px solid #30363D;border-radius:12px;padding:28px 32px;margin-bottom:24px;display:flex;align-items:center;gap:20px}}
  .header h1{{font-size:26px;color:#6366F1}}
  .header p{{color:#8B949E;font-size:13px;margin-top:4px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-bottom:24px}}
  .card{{background:#161B22;border:1px solid #30363D;border-radius:10px;padding:20px 24px}}
  .card h2{{color:#6366F1;font-size:13px;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;border-bottom:1px solid #30363D;padding-bottom:8px}}
  .row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #21262D}}
  .row .label{{color:#8B949E;font-size:12px}}
  .row .value{{color:#F0F6FC;font-weight:500;font-size:12px;max-width:55%;text-align:right;word-break:break-word}}
  table{{width:100%;border-collapse:collapse}}
  th{{color:#8B949E;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;padding:8px 12px;text-align:left;border-bottom:1px solid #30363D}}
  td{{padding:8px 12px;border-bottom:1px solid #21262D;font-size:12px;color:#F0F6FC}}
  tr:last-child td{{border:none}}
  .footer{{text-align:center;color:#6E7681;font-size:11px;margin-top:30px;padding-top:16px;border-top:1px solid #21262D}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div style="font-size:48px">🛡</div>
    <div>
      <h1>SmartFix AI — System Health Report</h1>
      <p>Generated: {ts} &nbsp;|&nbsp; Host: {info.get('hostname','—')} &nbsp;|&nbsp; OS: {info.get('windows_ver','—')}</p>
    </div>
  </div>

  <div class="grid">

    <div class="card">
      <h2>System Information</h2>
      <div class="row"><span class="label">CPU</span><span class="value">{info.get('cpu','—')}</span></div>
      <div class="row"><span class="label">CPU Cores</span><span class="value">{info.get('cpu_cores','—')}</span></div>
      <div class="row"><span class="label">RAM</span><span class="value">{info.get('ram_gb','—')} GB</span></div>
      <div class="row"><span class="label">GPU</span><span class="value">{info.get('gpu','—')}</span></div>
      <div class="row"><span class="label">Motherboard</span><span class="value">{info.get('mobo','—')}</span></div>
      <div class="row"><span class="label">Windows</span><span class="value">{info.get('windows_ver','—')}</span></div>
      <div class="row"><span class="label">Build</span><span class="value">{info.get('windows_build','—')}</span></div>
      <div class="row"><span class="label">Last Update</span><span class="value">{info.get('last_update','—')}</span></div>
      <div class="row"><span class="label">Uptime</span><span class="value">{info.get('uptime','—')} hrs</span></div>
    </div>

    <div class="card">
      <h2>Performance</h2>
      <div class="row"><span class="label">CPU Usage</span><span class="value">{cpu_pct:.1f}%</span></div>
      <div style="margin:4px 0 12px">{progress_bar(cpu_pct)}</div>
      <div class="row"><span class="label">RAM Used</span><span class="value">{info.get('ram_used','—')} GB</span></div>
      <div style="margin:4px 0 12px">{progress_bar(ram_pct)}</div>
      <div class="row"><span class="label">Disk C:</span><span class="value">{info.get('disk_c','—')}</span></div>
      <div style="margin:4px 0 12px">{progress_bar(disk_pct)}</div>
      <div class="row"><span class="label">Startup Items</span><span class="value">{info.get('startup_count','—')}</span></div>
      <div class="row"><span class="label">Errors (24h)</span>
        <span class="value">{"<span style='color:#FF3A3A;font-weight:bold'>" + str(info.get('recent_errors','0')) + " errors</span>" if int(info.get('recent_errors','0') or 0) > 0 else "<span style='color:#00D26A;font-weight:bold'>0 errors</span>"}</span>
      </div>
    </div>

    <div class="card">
      <h2>Security Status</h2>
      <div class="row"><span class="label">Windows Defender</span>
        <span class="value">{badge(str(info.get('defender','')).lower()=='true','ENABLED','DISABLED')}</span></div>
      <div class="row"><span class="label">Firewall</span>
        <span class="value">{badge(int(info.get('firewall','0') or 0)>0,'Active','OFF')}</span></div>
      <div class="row"><span class="label">TPM 2.0</span>
        <span class="value">{badge(str(info.get('tpm','')).lower()=='true','Present','Not Found')}</span></div>
      <div class="row"><span class="label">Secure Boot</span>
        <span class="value">{badge(str(info.get('secureboot','')).lower()=='true','Enabled','Disabled')}</span></div>
      <div class="row"><span class="label">Windows Activation</span>
        <span class="value">{badge(info.get('activation','')=='1','Activated','Check Needed')}</span></div>
    </div>

    <div class="card">
      <h2>Network</h2>
      <div class="row"><span class="label">Adapter</span><span class="value">{info.get('adapter','—')}</span></div>
      <div class="row"><span class="label">IP Address</span><span class="value">{info.get('ip','—')}</span></div>
      <div class="row"><span class="label">DNS Servers</span><span class="value">{info.get('dns','—')}</span></div>
    </div>

  </div>

  <div class="card" style="margin-bottom:24px">
    <h2>Critical Services</h2>
    <table>
      <tr><th>Service</th><th>Status</th></tr>
      {service_rows or "<tr><td colspan='2' style='color:#8B949E'>Could not retrieve services</td></tr>"}
    </table>
  </div>

  {"<div class='card'><h2>Recent Repair History</h2><table><tr><th>Time</th><th>Error</th><th>Category</th><th>Action</th></tr>" + history_html + "</table></div>" if history_html else ""}

  <div class="footer">SmartFix AI — B.E. Computer Engineering Major Project &nbsp;|&nbsp; Report generated {ts}</div>
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

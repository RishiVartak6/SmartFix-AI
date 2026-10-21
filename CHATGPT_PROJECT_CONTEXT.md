# 🛡️ SmartFix AI — Master Project Context & Architecture Guide
> **Complete documentation for ChatGPT / AI models to understand every aspect, mechanism, and code implementation of SmartFix AI.**

---

## 1. Executive Summary
**SmartFix AI** is an autonomous Windows system administration, monitoring, and automated repair software designed specifically for individual computers and **college/university computer lab networks**.

It combines:
1. **Real-time Local System Telemetry**: Monitors 170+ Windows operating system services, Windows Event Viewer crash logs, hardware metrics (CPU, RAM, Disk), and network states.
2. **Deterministic Automated PowerShell Repair Engine**: Implements 100% verified, administrative scripts to fix broken services, corrupted registries, blocked network adapters, broken compiler PATHs, and student lab errors.
3. **Local AI Autonomous Diagnosis & Self-Learning**: Powered by **Ollama (`llama3.2:1b`)** running 100% offline. Unknown, uncataloged application crashes are dynamically diagnosed by the LLM, generating a verified PowerShell fix that SmartFix executes and saves into a persistent learning database (`learned_errors.json`) for future automated reuse.
4. **Lab Monitor LAN Multi-PC Management**: Operates seamlessly in a **1 Admin (Teacher) + N Clients (Students)** setup over local Wi-Fi / Ethernet, featuring UDP auto-discovery, live lab grid telemetry, and 1-click remote administrative repair.
5. **Turnkey Standalone Windows Installer**: Packaged into a single, compact executable (`SmartFix_Setup.exe`, 2.15 MB, Inno Setup) that automatically downloads and silently installs Visual C++ 2022, Python 3.11, all required libraries, Ollama, the AI model, and firewall rules.

---

## 2. Real-World Context: College Computer Labs
In academic environments (engineering colleges, computer science labs, practical examination halls):
- 30 to 60 student computers run identical software (compilers, IDEs, web servers, databases).
- Typical daily failures paralyze student practical exams:
  - Students plug in flash drives and get blocked by corrupted write-protection policies.
  - Compilers (`gcc`, `python`, `javac`, `npm`) vanish from the terminal PATH.
  - Apache/XAMPP fails to start because Windows IIS (`W3SVC`) binds Port 80.
  - MySQL crashes and leaves ghost processes holding Port 3306.
  - Stale college proxies prevent internet access.
  - Dead motherboard CMOS batteries cause time drift, making all HTTPS websites throw `NET::ERR_CERT_DATE_INVALID`.
  - Task Manager or CMD gets disabled by student pranks or malware.
  - Unplugged projectors leave monitors stuck on a black screen.
  - C: drive fills to 0 MB free due to accumulated student temp files.
- **SmartFix AI solves this entire class of problems with zero IT staff intervention.**

---

## 3. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **GUI Framework** | `PyQt6` (Qt 6.6+) | Windows 11 Fluent Dark UI, asynchronous signals, toast popups, metric charts |
| **System Programming** | Python 3.10 / 3.11 | Core monitor threads, socket networking, repair dispatcher |
| **Windows API** | `pywin32` (`win32evtlog`, `win32api`, `win32gui`) | Querying Event Viewer logs, UAC elevation, COM objects |
| **Hardware & Process Telemetry**| `psutil`, `WMI` | CPU %, RAM %, Disk %, process iteration, physical disk health |
| **Repair Execution Subsystem** | Windows PowerShell 5.1+ / CMD | High-privilege administrative script execution with `-ExecutionPolicy Bypass` |
| **Local AI Engine** | Ollama (`llama3.2:1b` / `llama3`) via `httpx` | Local neural network inference on `http://localhost:11434` (offline, private) |
| **Network Protocol** | Custom JSON-framed TCP/UDP sockets | TCP Port 7771 (status & remote repair), UDP Port 7772 (beacon auto-discovery) |
| **Data Persistence** | SQLite (`smartfix_history.db`) & JSON | Repair logs, learned repair rules, seat configuration |
| **Installer Compiler** | Inno Setup 6 (`ISCC.exe`) | LZMA2 ultra-compressed self-contained setup wizard |
| **Elevated Launcher** | C# .NET Executable (`SmartFix AI.exe`) | Windows UAC `requireAdministrator` native stub launcher |

---

## 4. Lab Monitor Architecture (1 Admin + N Clients)

```
                       ┌────────────────────────────────────────────────────────┐
                       │               TEACHER / ADMIN PC (Port 7771)           │
                       │  - Listens on UDP 7772 for student beacons             │
                       │  - Displays live Lab Grid (Seat, IP, CPU, RAM, Errors) │
                       │  - Sends 1-Click Remote Repair JSON commands           │
                       └────────────────────────▲───────────────────────────────┘
                                                │
                               TCP 7771 Commands / UDP 7772 Beacon
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         │                                      │                                      │
┌────────┴──────────┐                  ┌────────┴──────────┐                  ┌────────┴──────────┐
│   CLIENT: PC-01   │                  │   CLIENT: PC-02   │                  │   CLIENT: PC-09   │
│ - BackgroundAgent │                  │ - BackgroundAgent │                  │ - BackgroundAgent │
│ - Broadcasts UDP  │                  │ - Broadcasts UDP  │                  │ - Broadcasts UDP  │
│ - Executes Repair │                  │ - Executes Repair │                  │ - Executes Repair │
└───────────────────┘                  └───────────────────┘                  └───────────────────┘
```

### Protocol & Message Types (`monitor/lab_config.py`):
All messages are JSON objects terminated by `\n`:
- `MSG_PING` / `MSG_PONG`: Liveness heartbeat check.
- `MSG_STATUS`: Client sends seat name, IP, CPU, RAM, Disk %, and active error array to Admin.
- `MSG_REPAIR`: Admin sends `{"repair_id": "...", "error_id": "..."}` to Client.
- `MSG_REPAIR_RESULT`: Client executes the repair script locally and returns success status, execution time, and output log.

---

## 5. Error Detection & Catalog (`monitor/error_catalog.py`)
SmartFix maintains a catalog of **170 system and application errors**, categorized into:
- **College Lab Practical Errors** (10 errors: USB locks, proxy, XAMPP, MySQL, Compilers, NTP, temps)
- **Windows Core Services** (Update, Spooler, Search, Audio, BITS, DHCP, EventLog, WMI, Hyper-V, VSS)
- **Networking & Connectivity** (DNS failure, gateway drop, proxy conflict, socket corruption)
- **System Integrity & Storage** (SFC corruption, BCD/Bootmgr missing, NTFS chkdsk, SMART warnings)
- **Developer & Third-Party Apps** (VS Code, Chrome, Teams, Discord, Office Click-to-Run, Valorant Vanguard)

### Detection Engine (`monitor/monitor.py`):
Runs in daemon background threads:
1. `_loop_services()`: Iterates `psutil.win_service_iter()` every 30s to detect stopped critical services.
2. `_loop_events()`: Reads Windows Event Viewer `System` and `Application` logs via `win32evtlog` for Event IDs (e.g. 1000 Application Error, 7000 Service Control Manager error, BugChecks).
3. `_loop_metrics()`: Inspects hardware thresholds (RAM > 92%, Disk < 10%, CPU lock).

---

## 6. How Errors are Actually Solved (`monitor/repair_engine.py`)
Repairs are NOT mocked. SmartFix runs with **Administrator elevation** and executes real PowerShell scripts:

```python
def _run_ps(script: str, timeout: int = 120) -> Tuple[bool, str]:
    result = subprocess.run(
        ["powershell", "-NonInteractive", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True, text=True, timeout=timeout,
        creationflags=0x08000000  # CREATE_NO_WINDOW
    )
    return result.returncode == 0, (result.stdout + result.stderr).strip()
```

### Specific Repair Implementations:
1. **USB Storage Access (`lab_fix_usb_storage`)**:
   Sets `HKLM\SYSTEM\CurrentControlSet\Services\USBSTOR` `Start = 3`, sets `StorageDevicePolicies\WriteProtect = 0`, and executes `pnputil /scan-devices`.
2. **Task Manager & CMD Unlock (`lab_unlock_taskmgr_cmd`)**:
   Deletes `DisableTaskMgr`, `DisableCMD`, and `DisableRegistryTools` from HKCU and HKLM policies.
3. **College Proxy Reset (`lab_reset_proxy_settings`)**:
   Sets WinINET `ProxyEnable = 0`, clears `ProxyServer`, runs `netsh winhttp reset proxy` and `ipconfig /flushdns`.
4. **Apache / XAMPP Port 80 Conflict (`lab_fix_apache_port_conflict`)**:
   Disables Windows IIS (`W3SVC`) and BranchCache, identifies conflicting process PID on port 80, and terminates it.
5. **MySQL Port 3306 Locked (`lab_fix_mysql_port_locked`)**:
   Finds owning PID on TCP port 3306 via `Get-NetTCPConnection`, terminates ghost `mysqld.exe`, and restarts MySQL service.
6. **Compiler PATH Restoration (`lab_restore_compiler_paths`)**:
   Auto-discovers `C:\MinGW\bin`, `C:\Python*`, Java JDK `bin`, Node.js, and Git directories and appends them to System and User `PATH`.
7. **Windows Update Reset (`reset_windows_update_components`)**:
   Stops `wuauserv`, `cryptsvc`, `bits`; renames `SoftwareDistribution` and `catroot2`; restarts services.
8. **Network Winsock & TCP/IP Reset (`reset_winsock_and_ip`)**:
   Executes `netsh winsock reset`, `netsh int ip reset`, and restarts DHCP client.

---

## 7. Autonomous AI Diagnostics & Self-Learning (`monitor/llm_assistant.py` + `monitor/learned_repairs.py`)
For unknown, novel application crashes (e.g., student C++/Java code memory fault `0xc0000005`):
1. **Model Discovery**: Dynamically queries `http://localhost:11434/api/tags` to detect installed models (`llama3.2:1b`, `llama3`).
2. **Diagnosis & Remediation**: Sends crash context, faulting module, and exception code to the local Ollama LLM with a strict prompt requiring a diagnosis and a ````powershell ... ```` script block.
3. **Execution**: The user reviews the AI explanation in the UI and clicks **"🤖 Execute AI Generated Fix"**.
4. **Self-Learning Persistence**: When the script executes successfully, SmartFix saves the error signature and script into `data/learned_errors.json`.
5. **Auto-Integration**: `execute_repair()` automatically checks `load_learned_errors()`. Next time the same error occurs, SmartFix resolves it instantly without querying the AI again.
6. **Heuristic Fallback**: If Ollama is offline or downloading, an autonomous expert heuristic fallback provides instant diagnosis and verified remediation scripts so the system never fails.

---

## 8. Presentation & Judge Demo Mode (`monitor/demo_mode.py`)
Designed for hackathon judges and lab practical demonstrations:
- Simulates real Windows service failures (Print Spooler, Windows Audio, Search, BITS, USB lock, Proxy lock) safely.
- Triggers a slide-in **Windows 11 Toast Popup** in the bottom-right corner with a 30s countdown.
- Clicking **"Fix Now"** runs the real repair, restores the service, updates the dashboard counter from 0 to 1, and marks the error resolved.

---

## 9. Installer & Packaging Pipeline (`SmartFix_Installer.iss` & `install_helper.ps1`)
- **Executable**: `dist/installer/SmartFix_Setup.exe` (2.15 MB, Inno Setup 6).
- **Silent Runtime Provisioning**:
  - Checks & installs Microsoft Visual C++ 2015–2022 x64.
  - Checks & installs Python 3.11.9 (64-bit) with `PATH` and `pip`.
  - Upgrades `pip` and installs `PyQt6`, `psutil`, `httpx`, `pywin32` (with `pywin32_postinstall.py`), `WMI`, `Pillow`, `pystray`, `plyer`.
  - Installs Ollama AI engine and pulls `llama3.2:1b` (1.3 GB compact high-speed model).
  - Configures Windows Defender Firewall inbound/outbound rules for ports 7771 & 7772.
  - Registers auto-start on Windows boot.

---

## 10. File-by-File Codebase Directory Map

```
SmartFix/
│
├── smartfix_app.py          # Core PyQt6 UI: MainWindow, Navigation Stack, StatCards, Toast Popups, Lab Page
├── SmartFix AI.exe          # C# .NET elevated launcher stub with UAC requireAdministrator manifest
├── BUILD_INSTALLER.bat      # 1-Click builder script running Inno Setup (ISCC.exe)
├── SmartFix_Installer.iss   # Inno Setup compiler script configuring files, registry, and tasks
├── install_helper.ps1       # Silent post-install PowerShell script provisioning Python, Ollama, model, firewall
├── requirements.txt         # Python library dependencies
├── README.md                # Project documentation
├── CHATGPT_PROJECT_CONTEXT.md # Master context guide for AI models
│
├── monitor/                 # Core engine package
│   ├── __init__.py          # Package initialization
│   ├── monitor.py           # BackgroundMonitor: multi-threaded service/event/metric polling engine
│   ├── error_catalog.py     # 170 Catalog errors, severities, descriptions, detection rules
│   ├── repair_engine.py     # 100% verified PowerShell repair functions + execute_repair() dispatcher
│   ├── repair_advanced.py   # BCD, Bootmgr, WMI salvage, SFC/DISM, registry repairs
│   ├── difficult_errors.py  # BSOD bugcheck definitions & memory dump analyzers
│   ├── lab_config.py        # Lab Monitor protocol (JSON framing), ports (7771, 7772), config persistence
│   ├── lab_agent.py         # Client Agent: UDP 7772 broadcaster & TCP 7771 command listener
│   ├── lab_admin.py         # Admin Manager: UDP discovery listener, client health polling, remote fix sender
│   ├── llm_assistant.py     # Local Ollama AI client (dynamic model detection + heuristic fallback)
│   ├── learned_repairs.py   # AI self-learning database manager (learned_errors.json)
│   ├── ai_dialog.py         # AIAssistantDialog: interactive AI diagnosis & script execution UI
│   ├── demo_mode.py         # DemoController & DemoScenario: safe error simulation engine
│   ├── demo_window.py       # Standalone demo selector window
│   ├── history.py           # SQLite database logger (smartfix_history.db)
│   ├── network_diag.py      # Ping, DNS, HTTP latency, and socket diagnostic routines
│   └── system_report.py     # HTML system health & diagnostic report exporter
│
└── data/                    # Runtime state & databases (auto-created)
    ├── smartfix_history.db  # SQLite database of detected & repaired errors
    ├── learned_errors.json  # Learned error signatures and AI-generated repair scripts
    └── lab_config.json      # Persistent lab seat name and role (admin/client)
```

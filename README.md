# 🛡 SmartFix AI — Intelligent Windows Error Monitor & Auto-Repair

> **Autonomous Windows error detection, diagnosis, and repair — powered by Llama 3 AI**

SmartFix AI runs silently in the background, monitors your Windows system for 150+ known errors, and offers one-click automated repairs. For unknown errors, it uses a local AI model (Llama 3 via Ollama) to generate and execute a custom PowerShell fix — which is then saved and reused forever.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Real-time Monitoring** | Watches Windows services, Event Log, CPU/RAM/Disk metrics continuously |
| ⚡ **150+ Hardcoded Errors** | Covers Windows Update, Network, Security, Storage, Applications, and more |
| 🤖 **AI Diagnosis** | Uses Llama 3 (local, private) to diagnose and fix unknown errors |
| 🧠 **Self-Learning** | AI-generated fixes are saved and reused on future occurrences |
| 🔔 **Smart Notifications** | CRITICAL errors trigger a clean toast popup — no spam |
| 🛠 **One-Click Repair** | PowerShell repair engine fixes errors automatically with admin rights |
| 📊 **System Dashboard** | Live CPU, RAM, Disk, Network, and service health overview |
| 🌐 **Network Diagnostics** | Full network connectivity and DNS resolution tests |
| 📄 **System Report** | Generates a detailed HTML system health report |
| 🎭 **Demo Mode** | Simulate real Windows errors to see SmartFix in action |

---

## 🚀 Quick Install (End Users)

1. Download **`SmartFix_Setup.exe`** from [Releases](https://github.com/RishiVartak6/SmartFix-AI/releases)
2. Double-click and follow the installer wizard
3. The installer automatically downloads and sets up:
   - Python 3.11
   - All required libraries (PyQt6, psutil, httpx)
   - Ollama AI engine
   - Llama 3 model (~4.7 GB — requires internet during setup)
4. SmartFix AI launches automatically and runs in the system tray

> **Requirements:** Windows 10/11 (64-bit) · Internet during install · 8 GB RAM recommended

---

## 🛠 Developer Setup

```bash
# Clone the repository
git clone https://github.com/RishiVartak6/SmartFix-AI.git
cd SmartFix-AI

# Install dependencies
pip install PyQt6 psutil httpx pywin32

# Run as Administrator (required for service monitoring)
python smartfix_app.py
```

### AI Features (Optional)
```bash
# Install Ollama from https://ollama.com
ollama pull llama3
ollama serve
```

---

## 🏗 Project Structure

```
SmartFix-AI/
├── smartfix_app.py          ← Main application (PyQt6 UI + system tray)
├── SmartFix AI.exe          ← C# launcher (production entry point)
├── monitor/
│   ├── monitor.py           ← Background monitoring threads
│   ├── error_catalog.py     ← 150+ Windows error definitions
│   ├── repair_engine.py     ← PowerShell repair executor
│   ├── repair_advanced.py   ← Advanced repair strategies
│   ├── difficult_errors.py  ← Complex error patterns
│   ├── ai_dialog.py         ← AI Diagnosis dialog
│   ├── llm_assistant.py     ← Ollama/Llama 3 interface
│   ├── learned_repairs.py   ← AI self-learning persistence
│   ├── demo_mode.py         ← Demo scenario engine
│   ├── demo_window.py       ← Demo UI window
│   ├── history.py           ← Repair history database
│   ├── network_diag.py      ← Network diagnostics
│   └── system_report.py     ← HTML report generator
├── BUILD_INSTALLER.bat      ← Rebuild SmartFix_Setup.exe
├── SmartFix_Installer.iss   ← Inno Setup installer script
└── install_helper.ps1       ← Silent dependency installer
```

---

## 🔐 How It Works

```
Windows error occurs
        ↓
BackgroundMonitor detects it (services / Event Log / metrics)
        ↓
Alert shown in dashboard + CRITICAL popup notification
        ↓
User clicks "Fix Now"
        ↓
Known error → PowerShell repair script executes
Unknown error → Llama 3 AI diagnoses → generates fix → executes → saved for future
```

---

## 📦 Building the Installer

```bash
# Requires Inno Setup 6 (auto-installed if missing)
BUILD_INSTALLER.bat
# Output: dist\installer\SmartFix_Setup.exe
```

---

## 🎓 Academic Project

Developed as a **B.E. Final Year Major Project** — Autonomous Windows System Repair using Local LLM.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

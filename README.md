# SmartFix AI — Intelligent Windows Error Diagnosis and Troubleshooting System

> **B.Tech Computer Engineering Major Project**  
> **Aldel Education Trust's St. John College of Engineering and Management, Palghar**

SmartFix AI is an AI-assisted Windows troubleshooting and repair desktop application that helps users diagnose and resolve common Windows and application software errors safely.

---

## Key Features

- **Automated Diagnostic Collectors**: Gathers real-time telemetry from CPU, RAM, Disk, 12+ Windows Services, Event Viewer (Application & System error/warning logs), top processes, network adapters, and DNS resolvers.
- **Deterministic Heuristic Rule Engine**: Immediate matching of known critical Windows failure patterns (Stopped services, DNS resolution failure, excessive RAM/CPU leaks, application crashes).
- **Local AI Reasoning with Ollama**: Integrates local open-weight instruct models (e.g. Qwen 2.5 / 3 8B) for natural language reasoning without requiring cloud API keys.
- **Strict Security Guardrails**: The LLM is restricted to choosing from an allowlisted **Repair Registry** of predefined PowerShell scripts. It can never generate or execute arbitrary unvalidated shell commands.
- **Explicit User Approval Gate**: Every repair requires explicit user confirmation displaying the detected problem, root cause, confidence score, risk rating, and administrator privilege status.
- **Post-Repair Verification Engine**: Automatically tests service health, DNS sockets, or process statuses to confirm whether the fix succeeded.
- **Audit & Resolution History**: Full historical record of diagnostic sessions, user approvals, execution outputs, and verification results stored locally in SQLite (`smartfix.db`).
- **Viva Demo Playground**: 1-click test fault injection to easily demonstrate full-loop problem detection and recovery during project evaluations.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS / Fluent Glassmorphism UI, Lucide Icons, Electron |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 |
| **Telemetry** | `psutil`, `pywin32`, Windows Management Instrumentation (WMI), PowerShell 7 / Windows PowerShell |
| **AI / LLM** | Ollama (`qwen2.5:latest` / `qwen3:8b`), local JSON schema formatting, offline heuristic fallback |
| **Database** | SQLite 3 via SQLAlchemy async (`aiosqlite`) |

---

## Quickstart Guide

### Prerequisites
1. **Python 3.10+**: Ensure `python` and `pip` are installed and added to your `PATH`.
2. **Node.js 18+**: Ensure `node` and `npm` are installed.
3. **Ollama (Optional for AI reasoning)**: Download and run [Ollama](https://ollama.ai) with `ollama run qwen2.5:latest`. If Ollama is not running, SmartFix operates in deterministic offline Rule Engine mode.

---

### Installation & Launch

#### Option A: Automated PowerShell Setup (Recommended)
Open PowerShell in the project directory and run:
```powershell
.\scripts\setup.ps1
```

#### Option B: Manual Setup

1. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the FastAPI Backend:**
   ```powershell
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Install & Start Frontend:**
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
   Open your browser at `http://localhost:5173`.

---

## Running Unit & Integration Tests

Run the comprehensive pytest test suite covering collectors, rule engines, repair security allowlists, and FastAPI endpoints:
```powershell
python -m pytest tests/ -v
```

---

## Project Structure

```
SmartFix/
├── backend/
│   ├── main.py                     # FastAPI application entrypoint
│   ├── config.py                   # Pydantic settings & configuration
│   ├── api/                        # REST API routers
│   │   ├── system.py               # Telemetry & health endpoints
│   │   ├── diagnosis.py            # AI & rule diagnosis pipeline
│   │   ├── repairs.py              # Repair catalog & approval/execution
│   │   ├── history.py              # SQLite audit trail endpoints
│   │   ├── settings.py             # Ollama configuration
│   │   └── demo.py                 # Viva demonstration fault simulator
│   ├── collectors/                 # Windows diagnostic collectors
│   │   ├── system.py               # Hardware & OS telemetry
│   │   ├── events.py               # Windows Event Logs
│   │   ├── services.py             # Windows Service inspector
│   │   ├── processes.py            # Top CPU/RAM consumers
│   │   ├── network.py              # DNS & adapter status
│   │   ├── application.py          # App crashes & WER
│   │   └── drivers.py              # Device driver status
│   ├── diagnosis/                  # Reasoning & schema engine
│   │   ├── schemas.py              # Pydantic JSON schemas
│   │   ├── rule_engine.py          # Deterministic heuristic rules
│   │   ├── prompts.py              # System prompt & guardrails
│   │   └── llm_engine.py           # Ollama client & offline fallback
│   ├── repairs/                    # Validated Repair Registry
│   │   ├── registry.py             # 13 allowlisted safe repair scripts
│   │   ├── executor.py             # Sandboxed execution & timeout
│   │   └── verification.py         # Post-repair validation handlers
│   └── database/                   # SQLite persistence layer
│       ├── database.py             # Async SQLAlchemy engine
│       └── models.py               # Session, Diagnosis, Repair models
├── frontend/                       # Desktop UI
│   ├── src/
│   │   ├── components/             # Sidebar, Header, ApprovalModal, ExecutionModal
│   │   ├── pages/                  # Dashboard, Diagnose, Health, Repairs, History, Demo, Settings
│   │   ├── services/api.ts         # Backend API client
│   │   ├── types/index.ts          # TypeScript interfaces
│   │   ├── App.tsx                 # Main layout
│   │   └── index.css               # Fluent Glassmorphism Tailwind styling
│   └── electron/main.cjs           # Electron desktop wrapper
├── tests/                          # Automated Pytest suite
│   ├── test_collectors.py
│   ├── test_rules.py
│   ├── test_repairs.py
│   └── test_api.py
├── scripts/
│   └── setup.ps1                   # 1-click Windows setup script
├── docs/
│   └── architecture.md             # In-depth architectural design
├── .env.example
├── requirements.txt
└── README.md
```

---

## Authors & Project Details
- **Project**: SmartFix AI — Intelligent Windows Troubleshooting System
- **College**: St. John College of Engineering and Management, Palghar
- **Department**: Department of Computer Engineering
- **Team**: Chirag Patil, Neel Pawaskar, Rishi Vartak
- **Project Guide**: Priyanka Kamble

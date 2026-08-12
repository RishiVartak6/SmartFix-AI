import subprocess
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger("smartfix.api.demo")
router = APIRouter(prefix="/api/demo", tags=["Demo Playground"])

class FaultSimRequest(BaseModel):
    fault_type: str # "stop_print_spooler", "stop_time_service", "stop_bluetooth_service", "flush_dns_test"

@router.post("/simulate-fault")
async def simulate_fault(req: FaultSimRequest):
    """
    Safely injects a controllable fault for presentation and validation demonstration.
    """
    logger.info(f"Simulating demo fault: {req.fault_type}")
    
    script = ""
    if req.fault_type == "stop_print_spooler":
        script = "Stop-Service -Name Spooler -Force -ErrorAction SilentlyContinue; (Get-Service -Name Spooler).Status"
    elif req.fault_type == "stop_time_service":
        script = "Stop-Service -Name W32Time -Force -ErrorAction SilentlyContinue; (Get-Service -Name W32Time).Status"
    elif req.fault_type == "stop_bluetooth_service":
        script = "Stop-Service -Name bthserv -Force -ErrorAction SilentlyContinue; (Get-Service -Name bthserv).Status"
    elif req.fault_type == "flush_dns_test":
        script = "ipconfig /flushdns"
    else:
        raise HTTPException(status_code=400, detail="Unknown demo fault type")

    try:
        startupinfo = None
        if hasattr(subprocess, 'STARTUPINFO'):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 6

        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=10,
            startupinfo=startupinfo
        )
        return {
            "status": "success",
            "fault_type": req.fault_type,
            "message": f"Demonstration fault '{req.fault_type}' successfully triggered.",
            "output": proc.stdout.strip(),
            "stderr": proc.stderr.strip()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fault injection note: {str(e)} (Ensure app is running with appropriate rights if stopping services)"
        }

@router.post("/restore-all")
async def restore_all_services():
    """Restores all common demonstration services to running state."""
    ps_script = """
    Start-Service -Name Spooler, W32Time, bthserv -ErrorAction SilentlyContinue
    Get-Service -Name Spooler, W32Time, bthserv | Select-Object Name, Status
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
            timeout=10,
            startupinfo=startupinfo
        )
        return {
            "status": "success",
            "message": "All demonstration services restored to Running state.",
            "output": proc.stdout.strip()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

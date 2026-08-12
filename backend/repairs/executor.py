import subprocess
import ctypes
import time
import logging
from typing import Dict, Any
from backend.repairs.registry import get_repair_by_id
from backend.repairs.verification import verify_repair

logger = logging.getLogger("smartfix.executor")

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def execute_repair_workflow(repair_id: str) -> Dict[str, Any]:
    """
    Executes a predefined, validated repair workflow from the allowlisted registry.
    NEVER accepts or executes arbitrary LLM/user scripts.
    """
    start_time = time.time()
    repair = get_repair_by_id(repair_id)
    if not repair:
        return {
            "success": False,
            "repair_id": repair_id,
            "error": f"Security Violation: Repair ID '{repair_id}' is not in the validated repair registry.",
            "output": "",
            "verified": False,
            "verification_success": False,
            "verification_message": "Execution aborted due to untrusted repair ID."
        }

    script_content = repair.get("script", "").strip()
    requires_admin = repair.get("requires_admin", False)
    current_is_admin = is_admin()

    logger.info(f"Executing repair '{repair_id}' (Requires Admin: {requires_admin}, Current Admin: {current_is_admin})")

    # Timeout adjustment based on repair type
    timeout = 180 if repair_id in ["run_sfc_scan", "run_dism_repair"] else 30

    output = ""
    error_msg = ""
    success = False

    try:
        startupinfo = None
        if hasattr(subprocess, 'STARTUPINFO'):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 6

        # Standard execution command
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script_content]
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            startupinfo=startupinfo
        )
        
        output = proc.stdout.strip()
        if proc.stderr:
            error_msg = proc.stderr.strip()

        # Check return code
        if proc.returncode == 0:
            success = True
        else:
            if not error_msg:
                error_msg = f"Process exited with non-zero exit code: {proc.returncode}"

    except subprocess.TimeoutExpired:
        error_msg = f"Repair timed out after {timeout} seconds."
        success = False
    except Exception as e:
        error_msg = f"Execution exception: {str(e)}"
        success = False

    # Execute Post-Repair Verification
    verification_key = repair.get("verification", "")
    verification_result = verify_repair(verification_key)
    
    # If the execution succeeded or verification confirms healthy state
    final_success = verification_result.get("success", success)
    duration_ms = int((time.time() - start_time) * 1000)

    return {
        "success": final_success,
        "repair_id": repair_id,
        "repair_name": repair["name"],
        "requires_admin": requires_admin,
        "is_admin_active": current_is_admin,
        "output": output,
        "error": error_msg if not final_success else None,
        "verified": True,
        "verification_success": verification_result.get("success", False),
        "verification_message": verification_result.get("message", ""),
        "verification_details": verification_result.get("details", {}),
        "duration_ms": duration_ms
    }

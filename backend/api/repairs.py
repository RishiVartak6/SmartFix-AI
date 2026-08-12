import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database.database import get_db
from backend.database.models import RepairRecord, AuditLog, DiagnosisRecord
from backend.repairs.registry import get_all_repairs, get_repair_by_id
from backend.repairs.executor import execute_repair_workflow, is_admin
from backend.diagnosis.schemas import RepairApprovalRequest

logger = logging.getLogger("smartfix.api.repairs")
router = APIRouter(prefix="/api/repairs", tags=["Repairs"])

@router.get("")
async def list_available_repairs():
    """Returns the complete catalog of predefined, safe repair workflows."""
    return {
        "catalog": get_all_repairs(),
        "is_admin": is_admin()
    }

@router.get("/{repair_id}")
async def get_repair_details(repair_id: str):
    repair = get_repair_by_id(repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Repair ID not found in registry")
    return {**repair, "is_admin": is_admin()}

@router.post("/{repair_id}/approve")
async def approve_repair(
    repair_id: str,
    req: RepairApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Explicit User Approval Gate: Records approval before execution can begin.
    """
    repair = get_repair_by_id(repair_id)
    if not repair:
        raise HTTPException(status_code=400, detail=f"Invalid repair ID '{repair_id}'")

    audit = AuditLog(
        action="REPAIR_APPROVED_BY_USER",
        details=f"User approved execution of repair '{repair['name']}' (ID: {repair_id})",
        status="approved"
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "approved",
        "repair_id": repair_id,
        "repair_name": repair["name"],
        "message": "Repair approval registered. Ready to execute."
    }

@router.post("/{repair_id}/execute")
async def execute_repair(
    repair_id: str,
    req: RepairApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Executes an approved, allowlisted repair workflow and immediately validates via Verification Engine.
    """
    repair_meta = get_repair_by_id(repair_id)
    if not repair_meta:
        raise HTTPException(status_code=400, detail="Disallowed repair ID")

    repair_db_id = str(uuid.uuid4())
    logger.info(f"Starting execution of repair {repair_id} (Record ID: {repair_db_id})")

    # Execute validated repair
    exec_result = execute_repair_workflow(repair_id)

    # Persist repair history
    repair_record = RepairRecord(
        id=repair_db_id,
        diagnosis_id=req.diagnosis_id,
        repair_id=repair_id,
        repair_name=repair_meta["name"],
        status="success" if exec_result["success"] else "failed",
        requires_admin=repair_meta.get("requires_admin", False),
        execution_output=exec_result.get("output", ""),
        error_message=exec_result.get("error"),
        verified=exec_result.get("verified", True),
        verification_success=exec_result.get("verification_success", False),
        verification_message=exec_result.get("verification_message", ""),
        execution_duration_ms=exec_result.get("duration_ms", 0)
    )
    db.add(repair_record)

    audit = AuditLog(
        action="REPAIR_EXECUTED",
        details=f"Executed '{repair_meta['name']}'. Success: {exec_result['success']}. Verified: {exec_result['verification_success']}",
        status="success" if exec_result["success"] else "failure"
    )
    db.add(audit)

    await db.commit()

    return {
        "record_id": repair_db_id,
        "repair_id": repair_id,
        "repair_name": repair_meta["name"],
        "success": exec_result["success"],
        "execution_output": exec_result["output"],
        "error_message": exec_result["error"],
        "verified": exec_result["verified"],
        "verification_success": exec_result["verification_success"],
        "verification_message": exec_result["verification_message"],
        "verification_details": exec_result.get("verification_details", {}),
        "duration_ms": exec_result["duration_ms"]
    }

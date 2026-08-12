from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List

from backend.database.database import get_db
from backend.database.models import DiagnosticSession, DiagnosisRecord, RepairRecord

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("")
async def get_history_list(
    limit: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves chronological repair and diagnosis history logs."""
    # Query repair records
    repairs_res = await db.execute(
        select(RepairRecord).order_by(desc(RepairRecord.timestamp)).limit(limit)
    )
    repairs = repairs_res.scalars().all()

    # Query sessions
    sessions_res = await db.execute(
        select(DiagnosticSession).order_by(desc(DiagnosticSession.timestamp)).limit(limit)
    )
    sessions = sessions_res.scalars().all()

    formatted_repairs = []
    for r in repairs:
        formatted_repairs.append({
            "id": r.id,
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp else "",
            "repair_id": r.repair_id,
            "repair_name": r.repair_name,
            "status": r.status,
            "requires_admin": r.requires_admin,
            "verification_success": r.verification_success,
            "verification_message": r.verification_message,
            "execution_output": r.execution_output,
            "error_message": r.error_message,
            "duration_ms": r.execution_duration_ms
        })

    formatted_sessions = []
    for s in sessions:
        formatted_sessions.append({
            "id": s.id,
            "timestamp": s.timestamp.strftime("%Y-%m-%d %H:%M:%S") if s.timestamp else "",
            "mode": s.mode,
            "problem_description": s.problem_description,
            "status": s.status
        })

    return {
        "repairs": formatted_repairs,
        "sessions": formatted_sessions,
        "total_repairs": len(formatted_repairs),
        "total_sessions": len(formatted_sessions)
    }

@router.get("/repair/{record_id}")
async def get_repair_record(record_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(RepairRecord).where(RepairRecord.id == record_id))
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Repair record not found")
    
    return {
        "id": r.id,
        "timestamp": r.timestamp.isoformat() if r.timestamp else "",
        "repair_id": r.repair_id,
        "repair_name": r.repair_name,
        "status": r.status,
        "requires_admin": r.requires_admin,
        "verification_success": r.verification_success,
        "verification_message": r.verification_message,
        "execution_output": r.execution_output,
        "error_message": r.error_message,
        "duration_ms": r.execution_duration_ms
    }

@router.delete("/clear")
async def clear_history(db: AsyncSession = Depends(get_db)):
    """Clears repair logs and past sessions from SQLite database."""
    from sqlalchemy import delete
    await db.execute(delete(RepairRecord))
    await db.execute(delete(DiagnosisRecord))
    await db.execute(delete(DiagnosticSession))
    await db.commit()
    return {"status": "success", "message": "History cleared successfully."}

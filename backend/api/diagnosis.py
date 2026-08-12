import uuid
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database.database import get_db
from backend.database.models import DiagnosticSession, DiagnosisRecord, SystemSnapshot, AuditLog
from backend.diagnosis.schemas import DiagnoseRequest, DiagnosisSchema
from backend.diagnosis.llm_engine import generate_ai_diagnosis
from backend.collectors.collector_manager import collect_full_diagnostics

logger = logging.getLogger("smartfix.api.diagnosis")
router = APIRouter(prefix="/api/diagnosis", tags=["Diagnosis"])

@router.post("", response_model=dict)
@router.post("/diagnose", response_model=dict)
async def perform_diagnosis(req: DiagnoseRequest, db: AsyncSession = Depends(get_db)):
    """
    Orchestrates the diagnostic pipeline:
    1. Collects system diagnostics
    2. Runs rule engine + Ollama AI model
    3. Persists session and structured diagnoses to SQLite database
    4. Returns structured diagnosis cards
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Initiating diagnostic session {session_id} (Mode: {req.mode})")

    # 1. Collect diagnostic data
    diagnostics = collect_full_diagnostics(user_query=req.user_query)

    # 2. Run Hybrid Rule Engine + AI Engine
    diagnoses_list = await generate_ai_diagnosis(diagnostics, user_query=req.user_query)

    # 3. Create DB records
    session_record = DiagnosticSession(
        id=session_id,
        mode=req.mode,
        problem_description=req.user_query or "System Diagnostics Scan",
        status="completed"
    )
    db.add(session_record)

    # Add snapshot
    snapshot_record = SystemSnapshot(
        id=str(uuid.uuid4()),
        session_id=session_id,
        cpu_percent=diagnostics["system"]["cpu"]["usage_percent"],
        ram_percent=diagnostics["system"]["memory"]["usage_percent"],
        disk_percent=diagnostics["system"]["primary_disk_percent"],
        summary_json=json.dumps({
            "health_status": diagnostics["health_status"],
            "failed_services": [s["name"] for s in diagnostics["services"].get("failed_critical_services", [])],
            "dns_healthy": diagnostics["network"].get("dns_healthy")
        })
    )
    db.add(snapshot_record)

    # Add diagnoses
    saved_diagnoses = []
    for diag in diagnoses_list:
        diag_id = str(uuid.uuid4())
        conf_level = "high" if diag.confidence >= 0.8 else ("medium" if diag.confidence >= 0.5 else "low")
        
        diag_record = DiagnosisRecord(
            id=diag_id,
            session_id=session_id,
            problem=diag.problem,
            probable_root_cause=diag.probable_root_cause,
            confidence=diag.confidence,
            confidence_level=conf_level,
            severity=diag.severity,
            evidence_json=json.dumps(diag.evidence),
            recommended_repair_id=diag.recommended_repair_id,
            explanation=diag.explanation,
            diagnosed_by="hybrid"
        )
        db.add(diag_record)
        
        saved_diagnoses.append({
            "id": diag_id,
            "problem": diag.problem,
            "probable_root_cause": diag.probable_root_cause,
            "confidence": diag.confidence,
            "confidence_level": conf_level,
            "severity": diag.severity,
            "evidence": diag.evidence,
            "recommended_repair_id": diag.recommended_repair_id,
            "explanation": diag.explanation
        })

    # Log audit
    audit = AuditLog(
        action="DIAGNOSIS_SESSION_COMPLETED",
        details=f"Session {session_id}: Detected {len(saved_diagnoses)} issue(s).",
        status="success"
    )
    db.add(audit)

    await db.commit()

    return {
        "session_id": session_id,
        "diagnostics_summary": {
            "health_status": diagnostics["health_status"],
            "attention_reasons": diagnostics["attention_reasons"],
            "cpu_percent": diagnostics["system"]["cpu"]["usage_percent"],
            "memory_percent": diagnostics["system"]["memory"]["usage_percent"],
            "network_status": diagnostics["network"]["status"]
        },
        "diagnoses": saved_diagnoses
    }

@router.get("/{diagnosis_id}")
async def get_diagnosis_by_id(diagnosis_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DiagnosisRecord).where(DiagnosisRecord.id == diagnosis_id))
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")
    
    return {
        "id": diag.id,
        "session_id": diag.session_id,
        "timestamp": diag.timestamp.isoformat() if diag.timestamp else None,
        "problem": diag.problem,
        "probable_root_cause": diag.probable_root_cause,
        "confidence": diag.confidence,
        "confidence_level": diag.confidence_level,
        "severity": diag.severity,
        "evidence": diag.evidence,
        "recommended_repair_id": diag.recommended_repair_id,
        "explanation": diag.explanation
    }

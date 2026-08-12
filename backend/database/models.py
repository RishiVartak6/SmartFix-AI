import datetime
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.database import Base

class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id = Column(String(36), primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    mode = Column(String(50), default="full_scan") # full_scan, user_query, specific_service, etc.
    problem_description = Column(Text, nullable=True)
    status = Column(String(50), default="completed") # pending, completed, failed
    
    diagnoses = relationship("DiagnosisRecord", back_populates="session", cascade="all, delete-orphan")
    snapshots = relationship("SystemSnapshot", back_populates="session", cascade="all, delete-orphan")

class DiagnosisRecord(Base):
    __tablename__ = "diagnoses"

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("diagnostic_sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    problem = Column(String(255), nullable=False)
    probable_root_cause = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    confidence_level = Column(String(20), default="high") # high, medium, low
    severity = Column(String(20), default="medium") # low, medium, high, critical
    evidence_json = Column(Text, default="[]") # JSON array of string evidences
    recommended_repair_id = Column(String(100), nullable=True)
    explanation = Column(Text, nullable=False)
    diagnosed_by = Column(String(50), default="hybrid") # rule_engine, llm, hybrid

    session = relationship("DiagnosticSession", back_populates="diagnoses")
    repairs = relationship("RepairRecord", back_populates="diagnosis", cascade="all, delete-orphan")

    @property
    def evidence(self):
        try:
            return json.loads(self.evidence_json) if self.evidence_json else []
        except Exception:
            return []

class RepairRecord(Base):
    __tablename__ = "repairs"

    id = Column(String(36), primary_key=True, index=True)
    diagnosis_id = Column(String(36), ForeignKey("diagnoses.id"), nullable=True)
    repair_id = Column(String(100), nullable=False)
    repair_name = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="pending") # approved, executing, success, failed, skipped
    requires_admin = Column(Boolean, default=False)
    execution_output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Verification details
    verified = Column(Boolean, default=False)
    verification_success = Column(Boolean, default=False)
    verification_message = Column(Text, nullable=True)
    execution_duration_ms = Column(Integer, default=0)

    diagnosis = relationship("DiagnosisRecord", back_populates="repairs")

class SystemSnapshot(Base):
    __tablename__ = "system_snapshots"

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("diagnostic_sessions.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    cpu_percent = Column(Float, default=0.0)
    ram_percent = Column(Float, default=0.0)
    disk_percent = Column(Float, default=0.0)
    summary_json = Column(Text, default="{}")

    session = relationship("DiagnosticSession", back_populates="snapshots")

class AppSettings(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(String(50), default="info")

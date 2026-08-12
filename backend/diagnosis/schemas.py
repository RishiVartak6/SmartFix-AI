from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DiagnosisSchema(BaseModel):
    problem: str = Field(..., description="Clear, user-friendly problem title")
    probable_root_cause: str = Field(..., description="Identified root cause explanation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    severity: str = Field("medium", description="Severity level: low, medium, high, critical")
    evidence: List[str] = Field(default_factory=list, description="List of concrete system facts, event logs, or metrics")
    recommended_repair_id: Optional[str] = Field(None, description="Allowlisted repair ID from the repair registry")
    explanation: str = Field(..., description="Simple, clear non-technical explanation")

class DiagnoseRequest(BaseModel):
    mode: str = Field("full_scan", description="full_scan or user_query")
    user_query: Optional[str] = Field(None, description="Optional natural language problem description")
    app_context: Optional[str] = Field(None, description="Specific application name if applicable")

class RepairApprovalRequest(BaseModel):
    repair_id: str
    diagnosis_id: Optional[str] = None
    session_id: Optional[str] = None

class TestOllamaRequest(BaseModel):
    ollama_host: Optional[str] = None
    ollama_model: Optional[str] = None

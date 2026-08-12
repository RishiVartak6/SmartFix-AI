from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.config import settings
from backend.diagnosis.llm_engine import check_ollama_status
from backend.repairs.executor import is_admin

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class UpdateSettingsRequest(BaseModel):
    ollama_host: Optional[str] = None
    ollama_model: Optional[str] = None
    ollama_timeout: Optional[int] = None

@router.get("")
async def get_settings_info():
    ollama_status = await check_ollama_status()
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "ollama_host": settings.OLLAMA_HOST,
        "ollama_model": settings.OLLAMA_MODEL,
        "ollama_timeout": settings.OLLAMA_TIMEOUT_SECONDS,
        "ollama_status": ollama_status,
        "is_admin": is_admin(),
        "database_url": settings.DATABASE_URL
    }

@router.post("")
async def update_settings(req: UpdateSettingsRequest):
    if req.ollama_host is not None:
        settings.OLLAMA_HOST = req.ollama_host
    if req.ollama_model is not None:
        settings.OLLAMA_MODEL = req.ollama_model
    if req.ollama_timeout is not None:
        settings.OLLAMA_TIMEOUT_SECONDS = req.ollama_timeout

    ollama_status = await check_ollama_status()
    return {
        "status": "success",
        "message": "Settings updated successfully",
        "current_settings": {
            "ollama_host": settings.OLLAMA_HOST,
            "ollama_model": settings.OLLAMA_MODEL,
            "ollama_timeout": settings.OLLAMA_TIMEOUT_SECONDS,
            "ollama_status": ollama_status
        }
    }

@router.post("/test-ollama")
async def test_ollama_connection(host: Optional[str] = None):
    res = await check_ollama_status(host=host)
    return res

@router.get("/admin-status")
async def get_admin_status():
    admin = is_admin()
    return {
        "is_admin": admin,
        "elevation_notice": "Running with Administrator privileges" if admin else "Running with Standard User privileges. Some system repairs will prompt Windows UAC."
    }

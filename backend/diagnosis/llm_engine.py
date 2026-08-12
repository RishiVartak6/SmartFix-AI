import httpx
import json
import logging
import re
from typing import Optional, Dict, Any, List
from backend.config import settings
from backend.diagnosis.schemas import DiagnosisSchema
from backend.diagnosis.prompts import SYSTEM_PROMPT, format_diagnostic_prompt
from backend.diagnosis.rule_engine import evaluate_rules
from backend.repairs.registry import REPAIR_CATALOG

logger = logging.getLogger("smartfix.llm_engine")

async def check_ollama_status(host: Optional[str] = None) -> Dict[str, Any]:
    ollama_url = host or settings.OLLAMA_HOST
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{ollama_url}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "available": True,
                    "host": ollama_url,
                    "models": models,
                    "configured_model": settings.OLLAMA_MODEL,
                    "model_installed": any(settings.OLLAMA_MODEL in m for m in models)
                }
    except Exception as e:
        logger.warning(f"Ollama connection check failed: {e}")
    
    return {
        "available": False,
        "host": ollama_url,
        "models": [],
        "configured_model": settings.OLLAMA_MODEL,
        "model_installed": False
    }

async def generate_ai_diagnosis(
    diagnostics: Dict[str, Any],
    user_query: Optional[str] = None
) -> List[DiagnosisSchema]:
    """
    Executes AI Diagnosis using local Ollama model.
    Falls back gracefully to deterministic rule engine if Ollama is unavailable.
    """
    rule_results = evaluate_rules(diagnostics, user_query)
    
    ollama_status = await check_ollama_status()
    if not ollama_status["available"]:
        logger.info("Ollama is not running. Using deterministic rule engine diagnosis.")
        if rule_results:
            return rule_results
        
        # If no specific rule triggered and system is healthy
        return [DiagnosisSchema(
            problem="System Operates Within Normal Parameters",
            probable_root_cause="No critical service failures, memory bottlenecks, or DNS issues were detected during the scan.",
            confidence=0.90,
            severity="low",
            evidence=[
                f"Active Services: {diagnostics.get('services', {}).get('running_count')} running",
                f"CPU Load: {diagnostics.get('system', {}).get('cpu', {}).get('usage_percent')}%",
                f"RAM Usage: {diagnostics.get('system', {}).get('memory', {}).get('usage_percent')}%"
            ],
            recommended_repair_id=None,
            explanation="Your system health metrics and services are currently stable."
        )]

    # If Ollama is available, query the LLM with structured prompt
    prompt_text = format_diagnostic_prompt(diagnostics, user_query)
    
    try:
        async with httpx.AsyncClient(timeout=float(settings.OLLAMA_TIMEOUT_SECONDS)) as client:
            payload = {
                "model": settings.OLLAMA_MODEL,
                "system": SYSTEM_PROMPT,
                "prompt": prompt_text,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            }
            
            response = await client.post(f"{settings.OLLAMA_HOST}/api/generate", json=payload)
            if response.status_code == 200:
                resp_json = response.json()
                raw_response = resp_json.get("response", "").strip()
                
                # Parse JSON
                try:
                    parsed = json.loads(raw_response)
                    # Validate schema
                    validated = DiagnosisSchema.model_validate(parsed)
                    
                    # Validate repair ID exists in catalog
                    if validated.recommended_repair_id and validated.recommended_repair_id not in REPAIR_CATALOG:
                        logger.warning(f"LLM proposed invalid repair ID '{validated.recommended_repair_id}'. Resetting to None.")
                        validated.recommended_repair_id = None
                        
                    return [validated]
                except Exception as parse_err:
                    logger.error(f"Error parsing LLM JSON response: {parse_err}. Raw output: {raw_response[:200]}")
    except Exception as e:
        logger.warning(f"Ollama inference error or timeout: {e}. Falling back to Rule Engine.")

    # Fallback to rule engine
    if rule_results:
        return rule_results

    return [DiagnosisSchema(
        problem="System Diagnostics Completed",
        probable_root_cause="Diagnostic collectors completed inspection. No critical failure patterns were detected.",
        confidence=0.85,
        severity="low",
        evidence=["Diagnostic scan ran successfully"],
        recommended_repair_id=None,
        explanation="The system is running stably with no immediate corrective actions required."
    )]

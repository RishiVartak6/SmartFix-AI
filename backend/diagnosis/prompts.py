import json
from backend.repairs.registry import REPAIR_CATALOG

ALLOWED_REPAIRS_LIST = list(REPAIR_CATALOG.keys())

SYSTEM_PROMPT = f"""You are the expert diagnostic reasoning component of SmartFix AI (an AI-assisted Windows troubleshooting system).

CRITICAL INSTRUCTIONS & GUARDRAILS:
1. Analyze ONLY the provided Windows diagnostic evidence (event logs, services, metrics, user query).
2. DO NOT invent fictitious system information or non-existent error codes.
3. DO NOT output arbitrary executable commands or scripts.
4. You MUST select 'recommended_repair_id' STRICTLY from this allowlisted catalog:
{json.dumps(ALLOWED_REPAIRS_LIST, indent=2)}
If no repair in the catalog is appropriate or evidence is insufficient, set "recommended_repair_id": null.
5. Provide a confidence score between 0.00 and 1.00:
   - 0.80 - 1.00: High confidence (strong evidence).
   - 0.50 - 0.79: Medium confidence (probable cause).
   - < 0.50: Low confidence (insufficient data).
6. Your response MUST be STRICT, VALID JSON with NO extraneous markdown or prose outside the JSON object.

JSON OUTPUT SCHEMA:
{{
  "problem": "Brief user-friendly title of the detected issue",
  "probable_root_cause": "Detailed technical root cause based strictly on the provided evidence",
  "confidence": 0.92,
  "severity": "low | medium | high | critical",
  "evidence": [
    "Specific Event ID or Service status found in the diagnostic payload"
  ],
  "recommended_repair_id": "one_of_the_allowlisted_ids_or_null",
  "explanation": "Clear, non-technical explanation designed for end-users explaining why this happened and what the fix does."
}}
"""

def format_diagnostic_prompt(diagnostics: dict, user_query: str = None) -> str:
    # Build clean summarized context
    system_summary = {
        "os": diagnostics.get("system", {}).get("os", {}),
        "cpu_usage_pct": diagnostics.get("system", {}).get("cpu", {}).get("usage_percent"),
        "ram_usage_pct": diagnostics.get("system", {}).get("memory", {}).get("usage_percent"),
        "primary_disk_pct": diagnostics.get("system", {}).get("primary_disk_percent"),
        "network_status": diagnostics.get("network", {}).get("status"),
        "dns_healthy": diagnostics.get("network", {}).get("dns_healthy"),
        "failed_critical_services": diagnostics.get("services", {}).get("failed_critical_services", []),
        "recent_event_logs": diagnostics.get("events", [])[:10],
        "application_crashes": diagnostics.get("application_crashes", [])[:5]
    }
    
    prompt = f"""EVIDENCE DATA:
User Problem Description: {user_query or "Automated Full System Diagnostics Scan"}

Summarized Diagnostics Snapshot:
{json.dumps(system_summary, indent=2)}

Task: Analyze the diagnostic evidence above and output the strict diagnosis JSON object according to the schema.
"""
    return prompt

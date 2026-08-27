import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("smartfix.llm")


OLLAMA_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"

def is_ollama_available() -> bool:
    """Checks if the local Ollama server is running."""
    try:
        r = httpx.get("http://localhost:11434/", timeout=2.0)
        return r.status_code == 200
    except httpx.RequestError:
        return False

def check_model_exists() -> bool:
    """Checks if the target model is downloaded in Ollama."""
    try:
        r = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if r.status_code == 200:
            models = r.json().get("models", [])
            for m in models:
                if m.get("name", "").startswith(OLLAMA_MODEL):
                    return True
        return False
    except httpx.RequestError:
        return False

def analyze_unknown_error(error_info: Dict[str, Any]) -> str:
    """
    Sends the unknown error details to the local LLM and asks for a diagnosis 
    and manual fix steps.
    """
    if not is_ollama_available():
        return "❌ Ollama is not running. Please start the Ollama application."
    
    if not check_model_exists():
        return f"❌ The '{OLLAMA_MODEL}' model is not installed. Open your terminal and run: ollama run {OLLAMA_MODEL}"

    prompt = f"""
You are SmartFix AI, an expert Windows System Administrator. 
The user has encountered an unknown system error that our automated scripts cannot fix. 
Please analyze this error and provide a short, clear explanation of what went wrong.
Crucially, if the error can be fixed via a script, write a precise PowerShell script to fix the issue. Wrap the script strictly in ```powershell and ``` tags.

Error Name: {error_info.get('name', 'Unknown Error')}
Category: {error_info.get('category', 'System')}
Technical Details: {error_info.get('technical', 'No technical details provided.')}

Response format:
**Diagnosis:** [Short explanation]

**PowerShell Fix:**
```powershell
# Script goes here
```
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        r = httpx.post(OLLAMA_URL, json=payload, timeout=60.0)
        r.raise_for_status()
        return r.json().get("response", "Error generating response.")
    except Exception as e:
        logger.error(f"LLM Generation failed: {e}")
        return f"❌ AI Assistant encountered an error while analyzing: {str(e)}"

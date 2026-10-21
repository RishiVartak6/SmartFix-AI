"""
SmartFix AI — Judge Demo Mode
Simulates real Windows errors so judges can see the full detection → alert → fix → verified flow.
Each demo is fully reversible and safe.
"""
import subprocess
import threading
import time
import logging
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger("smartfix.demo")


class DemoScenario:
    def __init__(self, error_id: str, name: str, description: str, inject_fn, cleanup_fn=None):
        self.error_id = error_id
        self.name = name
        self.description = description
        self._inject = inject_fn
        self._cleanup = cleanup_fn
        self.active = False

    def inject(self) -> bool:
        """Simulate the error. Returns True if successful."""
        try:
            result = self._inject()
            self.active = True
            return result
        except Exception as e:
            logger.error(f"Demo inject failed for {self.name}: {e}")
            return False

    def cleanup(self):
        """Revert the simulated error."""
        if self._cleanup and self.active:
            try:
                self._cleanup()
            except Exception as e:
                logger.error(f"Demo cleanup failed: {e}")
            self.active = False


def _stop_service(name: str) -> bool:
    """Stop a Windows service."""
    result = subprocess.run(
        ["sc", "stop", name],
        capture_output=True, text=True, timeout=15
    )
    logger.info(f"[DEMO] Stopped service: {name} — {result.returncode}")
    return result.returncode in (0, 1060, 1062)  # 1062 = not started


def _start_service(name: str):
    """Restart a Windows service."""
    subprocess.run(["sc", "start", name], capture_output=True, timeout=15)
    logger.info(f"[DEMO] Restarted service: {name}")


def _flush_dns() -> bool:
    result = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=10)
    return result.returncode == 0


# ─── Define Demo Scenarios ────────────────────────────────────

DEMO_SCENARIOS: Dict[str, DemoScenario] = {
    "print_spooler_not_running": DemoScenario(
        error_id="print_spooler_not_running",
        name="Print Spooler Service Failure",
        description="Stops the Print Spooler service. SmartFix detects it and offers to restart it.",
        inject_fn=lambda: _stop_service("Spooler"),
        cleanup_fn=lambda: _start_service("Spooler"),
    ),
    "windows_search_not_running": DemoScenario(
        error_id="windows_search_not_running",
        name="Windows Search Service Failure",
        description="Stops the Windows Search (WSearch) service. SmartFix detects it and restarts it.",
        inject_fn=lambda: _stop_service("WSearch"),
        cleanup_fn=lambda: _start_service("WSearch"),
    ),
    "windows_audio_not_running": DemoScenario(
        error_id="windows_audio_not_running",
        name="Windows Audio Service Failure",
        description="Stops the Windows Audio service. SmartFix detects and restores it.",
        inject_fn=lambda: _stop_service("AudioSrv"),
        cleanup_fn=lambda: _start_service("AudioSrv"),
    ),
    "bluetooth_service_not_running": DemoScenario(
        error_id="bluetooth_service_not_running",
        name="Bluetooth Service Failure",
        description="Stops the Bluetooth Support service. SmartFix detects and restarts it.",
        inject_fn=lambda: _stop_service("bthserv"),
        cleanup_fn=lambda: _start_service("bthserv"),
    ),
    "windows_time_not_running": DemoScenario(
        error_id="windows_time_not_running",
        name="Windows Time Service Failure",
        description="Stops the Windows Time (W32Time) service. SmartFix detects and restores it.",
        inject_fn=lambda: _stop_service("W32Time"),
        cleanup_fn=lambda: _start_service("W32Time"),
    ),
    "unknown_error_demo": DemoScenario(
        error_id="unknown_error_demo",
        name="Unknown Application Crash",
        description="Simulates a complex, undocumented crash in a 3rd party application (e.g., memory access violation).",
        inject_fn=lambda: True, 
        cleanup_fn=lambda: True,
    ),
    "windows_update_not_running": DemoScenario(
        error_id="windows_update_not_running",
        name="Windows Update Service Failure",
        description="Stops the Windows Update service (wuauserv). SmartFix detects and restarts it.",
        inject_fn=lambda: _stop_service("wuauserv"),
        cleanup_fn=lambda: _start_service("wuauserv"),
    ),
    "bits_not_running": DemoScenario(
        error_id="bits_not_running",
        name="BITS Service Failure",
        description="Stops the Background Intelligent Transfer Service. SmartFix detects and restores it.",
        inject_fn=lambda: _stop_service("BITS"),
        cleanup_fn=lambda: _start_service("BITS"),
    ),
    "lab_taskmgr_cmd_regedit_disabled": DemoScenario(
        error_id="lab_taskmgr_cmd_regedit_disabled",
        name="Task Manager / CMD Disabled by Policy",
        description="Simulates a student prank or malware locking Task Manager & Command Prompt. SmartFix unlocks all administrative tools.",
        inject_fn=lambda: True,
        cleanup_fn=lambda: True,
    ),
    "lab_proxy_stuck_offline": DemoScenario(
        error_id="lab_proxy_stuck_offline",
        name="College Proxy Refusing Connections",
        description="Simulates an unreachable college proxy blocking lab internet access. SmartFix resets proxy and restores LAN/WAN.",
        inject_fn=lambda: True,
        cleanup_fn=lambda: True,
    ),
    "lab_usb_storage_blocked": DemoScenario(
        error_id="lab_usb_storage_blocked",
        name="Student USB Flash Drive Blocked",
        description="Simulates USB storage write-protection and driver block. SmartFix restores USB permissions and scans hardware.",
        inject_fn=lambda: True,
        cleanup_fn=lambda: True,
    ),
}

DEMO_LIST = list(DEMO_SCENARIOS.values())


class DemoController:
    """
    Manages demo scenarios for judge presentations.
    Injects an error, waits for the monitor to detect it, then the fix flow runs normally.
    """

    def __init__(self, on_inject_error: Callable[[str], None]):
        """
        on_inject_error: callback that tells the monitor to immediately trigger an alert
                         for the given error_id (bypassing polling interval).
        """
        self.on_inject_error = on_inject_error
        self._active_scenario: Optional[DemoScenario] = None

    def run_demo(self, scenario_id: str, delay_seconds: float = 2.0):
        """
        Run a demo scenario in a background thread:
        1. Inject the error (stop service / etc.)
        2. Wait delay_seconds
        3. Notify monitor to trigger the alert immediately
        The repair flow (popup → fix → verify) runs normally from there.
        """
        scenario = DEMO_SCENARIOS.get(scenario_id)
        if not scenario:
            logger.warning(f"Unknown demo scenario: {scenario_id}")
            return

        self._active_scenario = scenario

        def _run():
            logger.info(f"[DEMO] Starting: {scenario.name}")
            success = scenario.inject()
            if not success:
                logger.warning(f"[DEMO] Injection failed for {scenario.name} — triggering virtual alert anyway")
            time.sleep(delay_seconds)
            # Tell monitor to send alert immediately
            self.on_inject_error(scenario.error_id)

        threading.Thread(target=_run, name="DemoRunner", daemon=True).start()

    def cleanup_active(self):
        """Clean up any active demo scenario."""
        if self._active_scenario:
            self._active_scenario.cleanup()
            self._active_scenario = None

    def get_all_scenarios(self) -> list:
        return DEMO_LIST

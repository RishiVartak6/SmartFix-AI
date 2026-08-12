from typing import Dict, Any, Optional

REPAIR_CATALOG: Dict[str, Dict[str, Any]] = {
    "restart_windows_update": {
        "id": "restart_windows_update",
        "name": "Restart Windows Update Services",
        "category": "Services & Updates",
        "risk": "low",
        "requires_admin": True,
        "description": "Restarts Windows Update (wuauserv), Background Intelligent Transfer Service (BITS), and Cryptographic Services.",
        "verification": "verify_windows_update_service",
        "script": """
            Stop-Service -Name wuauserv, bits, cryptsvc -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Start-Service -Name cryptsvc, bits, wuauserv
            Get-Service -Name wuauserv, bits, cryptsvc | Select-Object Name, Status
        """
    },
    "restart_print_spooler": {
        "id": "restart_print_spooler",
        "name": "Restart Print Spooler Service",
        "category": "Printing",
        "risk": "low",
        "requires_admin": True,
        "description": "Restarts the Print Spooler (Spooler) service and cleans hung print queues.",
        "verification": "verify_print_spooler_service",
        "script": """
            Stop-Service -Name Spooler -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Start-Service -Name Spooler
            Get-Service -Name Spooler | Select-Object Name, Status
        """
    },
    "restart_audio_service": {
        "id": "restart_audio_service",
        "name": "Restart Windows Audio Subsystem",
        "category": "Audio",
        "risk": "low",
        "requires_admin": True,
        "description": "Restarts Windows Audio (AudioSrv) and Audio Endpoint Builder services to restore sound output.",
        "verification": "verify_audio_service",
        "script": """
            Stop-Service -Name AudioEndpointBuilder, AudioSrv -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Start-Service -Name AudioEndpointBuilder, AudioSrv
            Get-Service -Name AudioSrv, AudioEndpointBuilder | Select-Object Name, Status
        """
    },
    "restart_bluetooth_service": {
        "id": "restart_bluetooth_service",
        "name": "Restart Bluetooth Support Service",
        "category": "Bluetooth",
        "risk": "low",
        "requires_admin": True,
        "description": "Restarts Bluetooth Support Service (bthserv) to reconnect paired peripherals.",
        "verification": "verify_bluetooth_service",
        "script": """
            Stop-Service -Name bthserv -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Start-Service -Name bthserv
            Get-Service -Name bthserv | Select-Object Name, Status
        """
    },
    "restart_time_service": {
        "id": "restart_time_service",
        "name": "Restart & Resync Windows Time Service",
        "category": "System",
        "risk": "low",
        "requires_admin": True,
        "description": "Restarts W32Time service and triggers a network clock resynchronization.",
        "verification": "verify_time_service",
        "script": """
            Stop-Service -Name W32Time -Force -ErrorAction SilentlyContinue
            Start-Service -Name W32Time
            w32tm /resync /nowait
            Get-Service -Name W32Time | Select-Object Name, Status
        """
    },
    "flush_dns": {
        "id": "flush_dns",
        "name": "Flush DNS Resolver Cache",
        "category": "Network",
        "risk": "low",
        "requires_admin": False,
        "description": "Clears and flushes the Windows DNS resolver cache to fix invalid host resolutions.",
        "verification": "verify_dns_resolution",
        "script": """
            ipconfig /flushdns
        """
    },
    "reset_winsock": {
        "id": "reset_winsock",
        "name": "Reset Winsock & TCP/IP Stack",
        "category": "Network",
        "risk": "medium",
        "requires_admin": True,
        "description": "Resets the Windows socket catalog and TCP/IP stack configuration to default factory state.",
        "verification": "verify_network_stack",
        "script": """
            netsh winsock reset
            netsh int ip reset
        """
    },
    "renew_ip": {
        "id": "renew_ip",
        "name": "Release and Renew DHCP IP Lease",
        "category": "Network",
        "risk": "low",
        "requires_admin": False,
        "description": "Releases current DHCP lease and requests a fresh IP address from the network router.",
        "verification": "verify_network_adapter",
        "script": """
            ipconfig /release
            Start-Sleep -Seconds 1
            ipconfig /renew
        """
    },
    "restart_explorer": {
        "id": "restart_explorer",
        "name": "Restart Windows Explorer Shell",
        "category": "UI & Explorer",
        "risk": "low",
        "requires_admin": False,
        "description": "Safely restarts the explorer.exe taskbar and desktop shell to resolve frozen UI or taskbar issues.",
        "verification": "verify_explorer_process",
        "script": """
            Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Start-Process explorer.exe
        """
    },
    "clear_store_cache": {
        "id": "clear_store_cache",
        "name": "Reset Microsoft Store Cache",
        "category": "Applications",
        "risk": "low",
        "requires_admin": True,
        "description": "Runs wsreset.exe tool to clean corrupt application cache files.",
        "verification": "verify_store_cache",
        "script": """
            Start-Process wsreset.exe -Wait
        """
    },
    "run_sfc_scan": {
        "id": "run_sfc_scan",
        "name": "System File Checker (SFC Scan)",
        "category": "System Integrity",
        "risk": "medium",
        "requires_admin": True,
        "description": "Scans Windows system files and repairs corrupted or missing protected files.",
        "verification": "verify_sfc_scan",
        "script": """
            sfc /scannow
        """
    },
    "run_dism_repair": {
        "id": "run_dism_repair",
        "name": "DISM Component Store Health Repair",
        "category": "System Integrity",
        "risk": "medium",
        "requires_admin": True,
        "description": "Checks and repairs Windows Component Store corruption using Deployment Image Servicing and Management.",
        "verification": "verify_dism_repair",
        "script": """
            DISM.exe /Online /Cleanup-Image /RestoreHealth
        """
    },
    "clean_temp_files": {
        "id": "clean_temp_files",
        "name": "Clean Windows & User Temp Cache",
        "category": "Performance",
        "risk": "low",
        "requires_admin": False,
        "description": "Safely removes obsolete temporary files to reclaim disk space and remove corrupted lockfiles.",
        "verification": "verify_temp_cleaned",
        "script": """
            Remove-Item -Path "$env:TEMP\\*" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Output "User temporary directory cache refreshed."
        """
    }
}

def get_repair_by_id(repair_id: str) -> Optional[Dict[str, Any]]:
    return REPAIR_CATALOG.get(repair_id)

def get_all_repairs() -> list:
    return list(REPAIR_CATALOG.values())

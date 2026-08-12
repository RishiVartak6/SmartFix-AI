import platform
import psutil
import datetime
import os

def collect_system_info() -> dict:
    """Collects hardware and OS metrics."""
    try:
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.datetime.now() - boot_time).total_seconds()
        uptime_hours = round(uptime_seconds / 3600, 2)
    except Exception:
        uptime_hours = 0.0

    # CPU info
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count_logical = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)
    cpu_freq = psutil.cpu_freq()
    current_freq = round(cpu_freq.current, 2) if cpu_freq else 0

    # Memory info
    mem = psutil.virtual_memory()
    memory_info = {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "available_gb": round(mem.available / (1024 ** 3), 2),
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "usage_percent": mem.percent
    }

    # Disk info
    disks = []
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "percent": usage.percent
            })
        except (PermissionError, Exception):
            continue

    # Primary disk usage
    primary_disk_percent = disks[0]["percent"] if disks else 0.0

    return {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "node": platform.node(),
            "uptime_hours": uptime_hours
        },
        "cpu": {
            "usage_percent": cpu_percent,
            "physical_cores": cpu_count_physical or 1,
            "logical_cores": cpu_count_logical or 1,
            "frequency_mhz": current_freq
        },
        "memory": memory_info,
        "disks": disks,
        "primary_disk_percent": primary_disk_percent
    }

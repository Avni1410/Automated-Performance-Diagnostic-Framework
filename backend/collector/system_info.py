"""
system_info.py

Collects static/basic system information such as OS details,
CPU count, total memory, disk capacity, hostname, and uptime.

This data changes rarely (unlike CPU% or memory%), so it's
gathered once and used as reference/context for later monitoring.
"""

import platform
import psutil
import time
from datetime import datetime, timedelta


def get_system_info() -> dict:
    """
    Returns a dictionary of basic system information.
    """
    # --- OS / platform info ---
    os_name = platform.system()          # e.g. "Linux", "Windows"
    os_version = platform.version()
    os_release = platform.release()
    hostname = platform.node()

    # --- CPU info ---
    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)

    # --- Memory info ---
    total_ram_bytes = psutil.virtual_memory().total
    total_ram_gb = round(total_ram_bytes / (1024 ** 3), 2)

    # --- Disk info (root partition) ---
    disk_usage = psutil.disk_usage("/")
    total_disk_gb = round(disk_usage.total / (1024 ** 3), 2)

    # --- Uptime ---
    boot_timestamp = psutil.boot_time()
    boot_time_readable = datetime.fromtimestamp(boot_timestamp).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    uptime_seconds = time.time() - boot_timestamp
    uptime_readable = str(timedelta(seconds=int(uptime_seconds)))

    return {
        "os_name": os_name,
        "os_release": os_release,
        "os_version": os_version,
        "hostname": hostname,
        "physical_cores": physical_cores,
        "logical_cores": logical_cores,
        "total_ram_gb": total_ram_gb,
        "total_disk_gb": total_disk_gb,
        "boot_time": boot_time_readable,
        "uptime": uptime_readable,
    }


if __name__ == "__main__":
    info = get_system_info()
    print("---- SYSTEM INFORMATION ----")
    for key, value in info.items():
        print(f"{key:16}: {value}")

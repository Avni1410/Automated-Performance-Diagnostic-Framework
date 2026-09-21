"""
file_descriptors.py

Monitors open file descriptors:
- Per-process FD counts
- System-wide total FD count

File descriptor counting is supported on Linux/macOS.
This project is intended to run under Linux/WSL2.
"""

import platform
import psutil

from backend.config import (
    FD_WARNING_THRESHOLD,
    FD_CRITICAL_THRESHOLD,
)


IS_LINUX_COMPATIBLE = platform.system() in ("Linux", "Darwin")


def get_fd_status(fd_count: int) -> str:
    """Classify file descriptor usage."""

    if fd_count >= FD_CRITICAL_THRESHOLD:
        return "CRITICAL"

    elif fd_count >= FD_WARNING_THRESHOLD:
        return "WARNING"

    else:
        return "NORMAL"


def get_process_fd_count(pid: int) -> dict:
    """
    Return the open file descriptor count for one process.
    """

    if not IS_LINUX_COMPATIBLE:
        return {
            "pid": pid,
            "error": (
                "File descriptor counting is only supported on "
                "Linux/macOS. Run this project under WSL2/Ubuntu."
            ),
        }

    try:
        proc = psutil.Process(pid)
        fd_count = proc.num_fds()

        return {
            "pid": pid,
            "process_name": proc.name(),
            "fd_count": fd_count,
            "status": get_fd_status(fd_count),
        }

    except psutil.NoSuchProcess:
        return {
            "pid": pid,
            "error": "Process no longer exists",
        }

    except psutil.AccessDenied:
        return {
            "pid": pid,
            "error": "Access denied",
        }


def get_system_fd_summary() -> dict:
    """
    Return system-wide file descriptor statistics.

    Processes that disappear or deny access are skipped.
    """

    if not IS_LINUX_COMPATIBLE:
        return {
            "error": (
                "File descriptor monitoring is only supported on "
                "Linux/macOS (this system is: "
                + platform.system()
                + "). Run this project under WSL2/Ubuntu."
            ),
            "total_fds": 0,
            "status": "UNKNOWN",
        }

    total_fds = 0
    per_process = []

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            fd_count = proc.num_fds()

            total_fds += fd_count

            per_process.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"],
                "fd_count": fd_count,
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    top_consumers = sorted(
        per_process,
        key=lambda p: p["fd_count"],
        reverse=True,
    )[:5]

    return {
        "total_fds": total_fds,
        "top_consumers": top_consumers,
        "status": get_fd_status(total_fds),
    }


if __name__ == "__main__":
    summary = get_system_fd_summary()

    print("---- FILE DESCRIPTOR SUMMARY ----")

    for key, value in summary.items():
        print(f"{key:16}: {value}")

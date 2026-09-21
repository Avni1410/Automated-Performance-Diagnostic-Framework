"""
threads.py

Provides thread-level detail for a given process, and identifies
processes with unusually high thread counts.

This builds on process.py rather than duplicating it — process.py
already reports num_threads per process; this module adds deeper
inspection for a specific PID plus a "high thread count" helper
that the diagnostic engine (Phase 9) will reuse.
"""

import psutil
from backend.config import HIGH_THREAD_COUNT_THRESHOLD


def get_thread_details(pid: int) -> dict:
    """
    Returns thread-level detail for a specific process ID.
    """
    try:
        proc = psutil.Process(pid)
        threads = proc.threads()

        thread_list = [
            {
                "thread_id": t.id,
                "user_time": t.user_time,
                "system_time": t.system_time,
            }
            for t in threads
        ]

        return {
            "pid": pid,
            "process_name": proc.name(),
            "thread_count": len(thread_list),
            "threads": thread_list,
            "high_thread_count": len(thread_list) >= HIGH_THREAD_COUNT_THRESHOLD,
        }

    except psutil.NoSuchProcess:
        return {"error": f"No process found with PID {pid}"}

    except psutil.AccessDenied:
        return {"error": f"Access denied when inspecting PID {pid}"}


def find_high_thread_processes(all_processes: list[dict]) -> list[dict]:
    """
    Given a process list from process.get_all_processes(),
    return processes with unusually high thread counts.
    """
    return [
        p for p in all_processes
        if p["num_threads"] >= HIGH_THREAD_COUNT_THRESHOLD
    ]


if __name__ == "__main__":
    import os

    current_pid = os.getpid()
    details = get_thread_details(current_pid)

    print("---- THREAD DETAILS (current process) ----")
    print(f"PID           : {details['pid']}")
    print(f"Name          : {details['process_name']}")
    print(f"Thread Count  : {details['thread_count']}")
    print(f"High Threads? : {details['high_thread_count']}")

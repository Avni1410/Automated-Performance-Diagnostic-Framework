"""
process.py

Collects information about running processes: PID, name, status,
CPU%, memory%, thread count, and parent PID.

Supports sorting and simple top-N views (top CPU / top memory),
which will later feed the diagnostic engine's "possible cause"
identification.
"""

import psutil


def get_all_processes() -> list[dict]:
    """
    Returns a list of dictionaries containing information
    about currently running processes.
    """
    processes = []

    for proc in psutil.process_iter(
        [
            "pid",
            "name",
            "status",
            "cpu_percent",
            "memory_percent",
            "num_threads",
            "ppid",
        ]
    ):
        try:
            info = proc.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "status": info["status"],
                "cpu_percent": round(info["cpu_percent"] or 0.0, 2),
                "memory_percent": round(info["memory_percent"] or 0.0, 2),
                "num_threads": info["num_threads"],
                "parent_pid": info["ppid"],
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    return processes


def get_top_processes_by_cpu(n: int = 5) -> list[dict]:
    """
    Returns the top N processes sorted by CPU usage.
    """
    processes = get_all_processes()

    return sorted(
        processes,
        key=lambda p: p["cpu_percent"],
        reverse=True
    )[:n]


def get_top_processes_by_memory(n: int = 5) -> list[dict]:
    """
    Returns the top N processes sorted by memory usage.
    """
    processes = get_all_processes()

    return sorted(
        processes,
        key=lambda p: p["memory_percent"],
        reverse=True
    )[:n]


def search_processes(name_query: str) -> list[dict]:
    """
    Returns processes whose name contains the given query.
    """
    processes = get_all_processes()

    query_lower = name_query.lower()

    return [
        p for p in processes
        if query_lower in p["name"].lower()
    ]


if __name__ == "__main__":
    print("---- TOP 5 PROCESSES BY CPU ----")

    for p in get_top_processes_by_cpu():
        print(p)

    print("\n---- TOP 5 PROCESSES BY MEMORY ----")

    for p in get_top_processes_by_memory():
        print(p)

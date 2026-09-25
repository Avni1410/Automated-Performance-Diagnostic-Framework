"""
rules.py

Rule-based diagnostic checks for the system monitoring framework.

Each rule receives:
    - recent_history: recent rows from system_metrics
    - processes: current process information

A rule returns a structured diagnostic dictionary when
a condition is detected, otherwise it returns None.

The engine reports possible causes rather than claiming certainty.
"""

from backend.config import (
    CPU_WARNING,
    CPU_CRITICAL,
    MEMORY_WARNING,
    MEMORY_CRITICAL,
    DISK_WARNING,
    DISK_CRITICAL,
    TOTAL_THREAD_WARNING_THRESHOLD,
    TOTAL_THREAD_CRITICAL_THRESHOLD,
    NETWORK_WARNING_THRESHOLD,
    NETWORK_CRITICAL_THRESHOLD,
    FD_WARNING_THRESHOLD,
    FD_CRITICAL_THRESHOLD,
    DIAGNOSTIC_DURATION_SECONDS,
    MONITOR_INTERVAL_SECONDS,
)

from backend.diagnostics.recommendations import get_recommendation


# Number of historical samples required to cover the configured
# diagnostic duration.
ROWS_FOR_DURATION_CHECK = max(
    1,
    DIAGNOSTIC_DURATION_SECONDS // MONITOR_INTERVAL_SECONDS
)


def _top_cpu_process(processes: list[dict]) -> dict | None:
    """Return the process currently using the most CPU."""

    valid = [
        p for p in processes
        if "cpu_percent" in p
        and isinstance(p["cpu_percent"], (int, float))
    ]

    if not valid:
        return None

    return max(valid, key=lambda p: p["cpu_percent"])


def _top_memory_process(processes: list[dict]) -> dict | None:
    """Return the process currently using the most memory."""

    valid = [
        p for p in processes
        if "memory_percent" in p
        and isinstance(p["memory_percent"], (int, float))
    ]

    if not valid:
        return None

    return max(valid, key=lambda p: p["memory_percent"])


def _top_thread_process(processes: list[dict]) -> dict | None:
    """Return the process with the highest thread count."""

    valid = [
        p for p in processes
        if "num_threads" in p
        and isinstance(p["num_threads"], (int, float))
    ]

    if not valid:
        return None

    return max(valid, key=lambda p: p["num_threads"])


def check_sustained_high_cpu(
    recent_history: list[dict],
    processes: list[dict],
) -> dict | None:
    """
    Detect CPU usage that remains above a warning or critical
    threshold for the configured diagnostic duration.
    """

    if len(recent_history) < ROWS_FOR_DURATION_CHECK:
        return None

    window = recent_history[-ROWS_FOR_DURATION_CHECK:]
    cpu_values = [row["cpu_percent"] for row in window]

    minimum_cpu = min(cpu_values)

    if minimum_cpu >= CPU_CRITICAL:
        severity = "CRITICAL"
    elif minimum_cpu >= CPU_WARNING:
        severity = "WARNING"
    else:
        return None

    top_process = _top_cpu_process(processes)

    if top_process:
        process_info = (
            f"Top CPU process: {top_process.get('name', 'unknown')} "
            f"(PID {top_process.get('pid', 'unknown')}) using "
            f"{top_process.get('cpu_percent', 0):.1f}% CPU."
        )
    else:
        process_info = "Top CPU process information unavailable."

    return {
        "severity": severity,
        "category": "cpu",
        "title": "Sustained high CPU usage detected",
        "evidence": (
            f"CPU usage remained at or above {minimum_cpu:.1f}% "
            f"for approximately {DIAGNOSTIC_DURATION_SECONDS} seconds. "
            f"{process_info}"
        ),
        "possible_cause": (
            "A CPU-intensive process or sustained workload may be "
            "contributing to the elevated CPU usage."
        ),
        "recommendation": get_recommendation("cpu"),
    }


def check_sustained_high_memory(
    recent_history: list[dict],
    processes: list[dict],
) -> dict | None:
    """
    Detect memory usage that remains above a warning or critical
    threshold for the configured diagnostic duration.
    """

    if len(recent_history) < ROWS_FOR_DURATION_CHECK:
        return None

    window = recent_history[-ROWS_FOR_DURATION_CHECK:]
    memory_values = [row["memory_percent"] for row in window]

    minimum_memory = min(memory_values)

    if minimum_memory >= MEMORY_CRITICAL:
        severity = "CRITICAL"
    elif minimum_memory >= MEMORY_WARNING:
        severity = "WARNING"
    else:
        return None

    top_process = _top_memory_process(processes)

    if top_process:
        process_info = (
            f"Top memory process: {top_process.get('name', 'unknown')} "
            f"(PID {top_process.get('pid', 'unknown')}) using "
            f"{top_process.get('memory_percent', 0):.1f}% memory."
        )
    else:
        process_info = "Top memory process information unavailable."

    return {
        "severity": severity,
        "category": "memory",
        "title": "Sustained high memory usage detected",
        "evidence": (
            f"Memory usage remained at or above {minimum_memory:.1f}% "
            f"for approximately {DIAGNOSTIC_DURATION_SECONDS} seconds. "
            f"{process_info}"
        ),
        "possible_cause": (
            "One or more memory-intensive processes may be contributing "
            "to sustained memory pressure."
        ),
        "recommendation": get_recommendation("memory"),
    }


def check_memory_pressure_combo(
    recent_history: list[dict],
    processes: list[dict],
) -> dict | None:
    """
    Detect a combination of high memory usage and increasing swap usage.
    """

    if len(recent_history) < ROWS_FOR_DURATION_CHECK:
        return None

    window = recent_history[-ROWS_FOR_DURATION_CHECK:]

    latest = window[-1]

    if latest["memory_percent"] < MEMORY_WARNING:
        return None

    swap_values = [row.get("swap_percent", 0.0) for row in window]

    if swap_values[-1] <= swap_values[0]:
        return None

    return {
        "severity": "CRITICAL",
        "category": "memory_pressure",
        "title": "Memory pressure detected",
        "evidence": (
            f"Memory usage is {latest['memory_percent']:.1f}% and "
            f"swap usage increased from {swap_values[0]:.1f}% to "
            f"{swap_values[-1]:.1f}% over approximately "
            f"{DIAGNOSTIC_DURATION_SECONDS} seconds."
        ),
        "possible_cause": (
            "The system may be experiencing RAM pressure and "
            "offloading memory pages to swap."
        ),
        "recommendation": get_recommendation("memory_pressure"),
    }


def check_high_disk_usage(
    recent_history: list[dict],
    processes: list[dict],
) -> dict | None:
    """
    Detect high current disk usage.
    """

    if not recent_history:
        return None

    latest = recent_history[-1]
    disk_usage = latest["disk_percent"]

    if disk_usage >= DISK_CRITICAL:
        severity = "CRITICAL"
    elif disk_usage >= DISK_WARNING:
        severity = "WARNING"
    else:
        return None

    return {
        "severity": severity,
        "category": "disk",
        "title": "High disk usage detected",
        "evidence": (
            f"Current disk usage is {disk_usage:.1f}%, "
            f"above the configured {severity.lower()} threshold."
        ),
        "possible_cause": (
            "Large files, logs, temporary files, or build artifacts "
            "may be contributing to high disk utilization."
        ),
        "recommendation": get_recommendation("disk"),
    }


def check_high_thread_count(
    recent_history: list[dict],
    processes: list[dict],
) -> dict | None:
    """
    Detect unusually high total system thread count.
    """

    if not recent_history:
        return None

    latest = recent_history[-1]
    total_threads = latest["thread_count"]

    if total_threads >= TOTAL_THREAD_CRITICAL_THRESHOLD:
        severity = "CRITICAL"
    elif total_threads >= TOTAL_THREAD_WARNING_THRESHOLD:
        severity = "WARNING"
    else:
        return None

    top_process = _top_thread_process(processes)

    if top_process:
        process_info = (
            f"Highest-thread process: {top_process.get('name', 'unknown')} "
            f"(PID {top_process.get('pid', 'unknown')}) with "
            f"{top_process.get('num_threads', 0)} threads."
        )
    else:
        process_info = "Highest-thread process information unavailable."

    return {
        "severity": severity,
        "category": "threads",
        "title": "High total thread count detected",
        "evidence": (
            f"Total system thread count is {total_threads}. "
            f"{process_info}"
        ),
        "possible_cause": (
            "One or more applications may be creating an unusually "
            "large number of threads."
        ),
        "recommendation": get_recommendation("threads"),
    }


def check_high_network_connections(
    recent_history: list[dict],
    processes: list[dict],
) -> dict | None:
    """
    Detect unusually high numbers of network connections.
    """

    if not recent_history:
        return None

    latest = recent_history[-1]
    connections = latest["network_connections"]

    if connections >= NETWORK_CRITICAL_THRESHOLD:
        severity = "CRITICAL"
    elif connections >= NETWORK_WARNING_THRESHOLD:
        severity = "WARNING"
    else:
        return None

    return {
        "severity": severity,
        "category": "network",
        "title": "High network connection count detected",
        "evidence": (
            f"Current network connection count is {connections}, "
            f"above the configured {severity.lower()} threshold."
        ),
        "possible_cause": (
            "A process may be maintaining an unusually large number "
            "of active network connections."
        ),
        "recommendation": get_recommendation("network"),
    }


def check_high_fd_count(
    recent_history: list[dict],
    processes: list[dict],
) -> dict | None:
    """
    Detect unusually high system-wide file descriptor usage.
    """

    if not recent_history:
        return None

    latest = recent_history[-1]
    fd_count = latest["file_descriptor_count"]

    if fd_count >= FD_CRITICAL_THRESHOLD:
        severity = "CRITICAL"
    elif fd_count >= FD_WARNING_THRESHOLD:
        severity = "WARNING"
    else:
        return None

    return {
        "severity": severity,
        "category": "file_descriptors",
        "title": "High file descriptor count detected",
        "evidence": (
            f"Current system file descriptor count is {fd_count}, "
            f"above the configured {severity.lower()} threshold."
        ),
        "possible_cause": (
            "One or more processes may have an unusually high number "
            "of open files or other file descriptors."
        ),
        "recommendation": get_recommendation("file_descriptors"),
    }


# All diagnostic rules executed by the analyzer.
ALL_RULES = [
    check_sustained_high_cpu,
    check_sustained_high_memory,
    check_memory_pressure_combo,
    check_high_disk_usage,
    check_high_thread_count,
    check_high_network_connections,
    check_high_fd_count,
]

"""
network.py

Collects network connection information:
- Total TCP/UDP connections
- Connection state breakdown
- Listening ports

Some systems may restrict access to connections belonging
to other users. Such permission errors are handled gracefully.
"""

import psutil

from backend.config import (
    NETWORK_WARNING_THRESHOLD,
    NETWORK_CRITICAL_THRESHOLD,
)


def get_network_status(connection_count: int) -> str:
    """Classify network usage based on connection count."""

    if connection_count >= NETWORK_CRITICAL_THRESHOLD:
        return "CRITICAL"

    elif connection_count >= NETWORK_WARNING_THRESHOLD:
        return "WARNING"

    else:
        return "NORMAL"


def get_network_metrics() -> dict:
    """
    Collect network connection information.

    Returns:
        dict containing:
        - total_connections
        - state_breakdown
        - listening_ports
        - status
    """

    try:
        connections = psutil.net_connections(kind="inet")

    except psutil.AccessDenied:
        return {
            "error": (
                "Access denied - elevated permissions may be "
                "required to see all connections."
            ),
            "total_connections": 0,
            "state_breakdown": {},
            "listening_ports": [],
            "status": "UNKNOWN",
        }

    state_counts = {}
    listening_ports = []

    for conn in connections:

        # UDP sockets may not have a TCP-style state.
        state = conn.status if conn.status else "NONE"

        state_counts[state] = state_counts.get(state, 0) + 1

        # Record ports where a process is listening.
        if conn.status == "LISTEN" and conn.laddr:
            listening_ports.append(conn.laddr.port)

    total_connections = len(connections)

    return {
        "total_connections": total_connections,
        "state_breakdown": state_counts,
        "listening_ports": sorted(set(listening_ports)),
        "status": get_network_status(total_connections),
    }


if __name__ == "__main__":

    metrics = get_network_metrics()

    print("---- NETWORK METRICS ----")

    for key, value in metrics.items():
        print(f"{key:18}: {value}")
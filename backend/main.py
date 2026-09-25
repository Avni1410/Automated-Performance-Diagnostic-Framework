"""
main.py

The monitoring loop: repeatedly collects metrics from our existing
collectors, stores them in the database, runs the diagnostic engine,
and prints a status line.

This does NOT reimplement any collection logic - it only calls
functions already defined in backend/collector/.
"""

import time
import logging

from backend.collector.cpu import get_cpu_metrics
from backend.collector.memory import get_memory_metrics
from backend.collector.disk import get_disk_metrics
from backend.collector.process import get_all_processes
from backend.collector.network import get_network_metrics
from backend.collector.file_descriptors import get_system_fd_summary

from backend.database.database import (
    init_db,
    insert_metrics,
    get_recent_metrics,
    insert_diagnostic_event,
)

from backend.diagnostics.analyzer import run_diagnostics

from backend.config import MONITOR_INTERVAL_SECONDS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def collect_and_store_once():
    """
    Performs one full collection cycle, stores the metrics,
    runs diagnostics, and stores any diagnostic events.

    Returns the collected values and diagnostic count so main()
    can print a summary.
    """

    try:
        # ---------------------------------------------------------
        # 1. Collect metrics from existing Phase 1-8 collectors
        # ---------------------------------------------------------

        cpu = get_cpu_metrics()
        memory = get_memory_metrics()
        disk = get_disk_metrics()
        processes = get_all_processes()
        network = get_network_metrics()
        fd_summary = get_system_fd_summary()

        # Total number of threads across all visible processes.
        total_threads = sum(
            p["num_threads"] for p in processes
        )

        # ---------------------------------------------------------
        # 2. Store current metrics
        # ---------------------------------------------------------

        insert_metrics(
            cpu_percent=cpu["total_percent"],
            memory_percent=memory["percent"],
            disk_percent=disk["percent"],
            swap_percent=memory["swap_percent"],
            process_count=len(processes),
            thread_count=total_threads,
            network_connections=network.get("total_connections", 0),
            file_descriptor_count=fd_summary.get("total_fds", 0),
        )

        # ---------------------------------------------------------
        # 3. Retrieve recent history for duration-based rules
        # ---------------------------------------------------------

        recent_history = get_recent_metrics(limit=50)

        # ---------------------------------------------------------
        # 4. Run the Phase 9 diagnostic engine
        # ---------------------------------------------------------

        diagnostics = run_diagnostics(
            recent_history=recent_history,
            processes=processes,
        )

        # ---------------------------------------------------------
        # 5. Store each diagnostic event
        # ---------------------------------------------------------

        for diagnostic in diagnostics:
            insert_diagnostic_event(**diagnostic)

            logger.warning(
                f"{diagnostic['severity']}: "
                f"{diagnostic['title']} | "
                f"{diagnostic['evidence']}"
            )

        # ---------------------------------------------------------
        # 6. Return summary for the monitoring log
        # ---------------------------------------------------------

        return {
            "cpu": cpu["total_percent"],
            "memory": memory["percent"],
            "swap": memory["swap_percent"],
            "disk": disk["percent"],
            "processes": len(processes),
            "threads": total_threads,
            "network": network.get("total_connections", 0),
            "fds": fd_summary.get("total_fds", 0),
            "diagnostics_triggered": len(diagnostics),
        }

    except Exception as e:
        logger.error(f"Collection cycle failed: {e}")
        return None


def main():
    init_db()

    logger.info(
        "Database initialized. Starting monitoring loop..."
    )

    logger.info(
        f"Monitoring interval: {MONITOR_INTERVAL_SECONDS} seconds"
    )

    logger.info("Press Ctrl+C to stop.")

    try:
        while True:
            summary = collect_and_store_once()

            if summary:
                logger.info(
                    f"CPU: {summary['cpu']}% | "
                    f"Memory: {summary['memory']}% | "
                    f"Swap: {summary['swap']}% | "
                    f"Disk: {summary['disk']}% | "
                    f"Processes: {summary['processes']} | "
                    f"Threads: {summary['threads']} | "
                    f"Network Connections: {summary['network']} | "
                    f"FDs: {summary['fds']} | "
                    f"Diagnostics: {summary['diagnostics_triggered']}"
                )

            time.sleep(MONITOR_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")


if __name__ == "__main__":
    main()
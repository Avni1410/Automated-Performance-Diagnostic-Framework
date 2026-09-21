"""
main.py

The monitoring loop: repeatedly collects metrics from our existing
collectors, stores them in the database, and prints a status line.

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
from backend.database.database import init_db, insert_metrics
from backend.config import MONITOR_INTERVAL_SECONDS
from backend.collector.file_descriptors import get_system_fd_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def collect_and_store_once():
    """
    Performs one full collection cycle and stores it in the database.
    Returns the collected values so main() can print a summary.
    """

    try:
        cpu = get_cpu_metrics()
        memory = get_memory_metrics()
        disk = get_disk_metrics()
        processes = get_all_processes()
        network = get_network_metrics()
        fd_summary = get_system_fd_summary()
        total_threads = sum(
            p["num_threads"] for p in processes
        )

        insert_metrics(
            cpu_percent=cpu["total_percent"],
            memory_percent=memory["percent"],
            disk_percent=disk["percent"],
            process_count=len(processes),
            thread_count=total_threads,
            network_connections=network.get("total_connections", 0),
            file_descriptor_count=fd_summary.get("total_fds", 0),
        )

        return {
            "cpu": cpu["total_percent"],
            "memory": memory["percent"],
            "disk": disk["percent"],
            "processes": len(processes),
            "threads": total_threads,
            "network": network.get("total_connections", 0),
            "fds": fd_summary.get("total_fds", 0),
        }

    except Exception as e:
        logger.error(f"Collection cycle failed: {e}")
        return None


def main():
    init_db()

    logger.info("Database initialized. Starting monitoring loop...")
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
                    f"Disk: {summary['disk']}% | "
                    f"Processes: {summary['processes']} | "
                    f"Threads: {summary['threads']} | "
                    f"Network Connections: {summary['network']}"
                    f" | FDs: {summary['fds']}"
                )

            time.sleep(MONITOR_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")


if __name__ == "__main__":
    main()

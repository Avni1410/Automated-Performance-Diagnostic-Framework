"""
recommendations.py

Centralized human-readable recommendations for the diagnostic engine.

The diagnostic rules identify a problem and category.
This module provides the corresponding recommended action.
"""

RECOMMENDATIONS = {
    "cpu": (
        "Investigate the process using the most CPU and determine "
        "whether the workload is expected or unexpected."
    ),

    "memory": (
        "Inspect the process using the most memory and consider "
        "restarting it if a memory leak is suspected."
    ),

    "memory_pressure": (
        "Close unused applications and investigate memory-heavy "
        "processes. Sustained swap usage can slow the system."
    ),

    "disk": (
        "Review large files, logs, temporary files, and build "
        "artifacts to identify opportunities to free disk space."
    ),

    "threads": (
        "Investigate the process with the highest thread count "
        "and determine whether the number of threads is expected."
    ),

    "network": (
        "Investigate the process with the most network connections "
        "and review whether the connection behavior is expected."
    ),

    "file_descriptors": (
        "Investigate processes with high open file counts for a "
        "possible file descriptor leak."
    ),
}


def get_recommendation(category: str) -> str:
    """
    Return the recommendation associated with a diagnostic category.

    If a category is not defined, return a generic recommendation.
    """

    return RECOMMENDATIONS.get(
        category,
        "Investigate the reported system condition and monitor it over time."
    )

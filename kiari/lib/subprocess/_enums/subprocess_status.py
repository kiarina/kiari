from enum import Enum


class SubprocessStatus(Enum):
    RUNNING = "RUNNING"
    """Process is currently running"""

    SUCCESS = "SUCCESS"
    """Process completed successfully (returncode = 0)"""

    CANCELLED = "CANCELLED"
    """Process was cancelled externally"""

    FAILURE = "FAILURE"
    """Process failed (returncode != 0)"""

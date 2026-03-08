# System Layer: System-level functionality
"""
System-level components for process management, scheduling, and error handling.
"""

# Import error handler components first (no circular dependencies)
from .error_handler import HealthChecker, RetryExhaustedError, record_error, retry_with_backoff
from .process_manager import start_qa_bot, stop_qa_bot
from .shutdown_manager import ShutdownManager, get_shutdown_manager


# Lazy import Scheduler to avoid circular dependencies with ai_client
def _get_scheduler():
    from .scheduler import Scheduler

    return Scheduler


__all__ = [
    "HealthChecker",
    "RetryExhaustedError",
    "ShutdownManager",
    "get_shutdown_manager",
    "record_error",
    "retry_with_backoff",
    "start_qa_bot",
    "stop_qa_bot",
    # Note: Import Scheduler directly from core.system.scheduler to avoid circular imports
]

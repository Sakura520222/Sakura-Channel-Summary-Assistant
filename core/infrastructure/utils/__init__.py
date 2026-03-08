# Infrastructure: Shared utilities
"""
Shared utility functions and constants.
"""

# Constants
from .constants import (
    BOT_STATE_PAUSED,
    BOT_STATE_RUNNING,
    BOT_STATE_SHUTTING_DOWN,
    CLEANUP_DAYS_DEFAULT,
    CONFIG_FILE,
    DATA_DIR,
    DATABASE_FILE,
    DEFAULT_LLM_BASE_URL,
    DEFAULT_LLM_MODEL,
    DEFAULT_LOG_LEVEL,
    DEFAULT_POLL_PROMPT,
    DEFAULT_PROMPT,
    DEFAULT_SUMMARY_DAY,
    DEFAULT_SUMMARY_HOUR,
    DEFAULT_SUMMARY_MINUTE,
    LAST_SUMMARY_FILE,
    LOG_LEVEL_MAP,
    POLL_OPTION_MAX_LENGTH,
    POLL_PROMPT_FILE,
    POLL_QUESTION_MAX_LENGTH,
    POLL_REGEN_THRESHOLD_DEFAULT,
    POLL_REGENERATIONS_FILE,
    PROMPT_FILE,
    RESTART_FLAG_FILE,
    RETRY_BASE_DELAY,
    RETRY_MAX_ATTEMPTS,
    RETRY_MAX_DELAY,
    SESSIONS_DIR,
    VALID_BOT_STATES,
    VALID_DAYS,
    VALID_FREQUENCIES,
)

# Date utilities
from .date_utils import extract_date_range_from_summary

# Exceptions
from .exceptions import (
    AIServiceError,
    BotError,
    ChannelNotFoundError,
    ConfigurationError,
    DatabaseError,
    InvalidScheduleError,
    PollGenerationError,
    TelegramAPIError,
    ValidationError,
)

# Message utilities
from .message_utils import format_schedule_info, split_long_message

# States
from .states import UserContext, get_user_context

# Version utilities
from .version_utils import compare_versions, get_local_version

__all__ = [
    # Constants
    "CLEANUP_DAYS_DEFAULT",
    "CONFIG_FILE",
    "DATABASE_FILE",
    "DATA_DIR",
    "DEFAULT_LLM_BASE_URL",
    "DEFAULT_LLM_MODEL",
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_POLL_PROMPT",
    "DEFAULT_PROMPT",
    "DEFAULT_SUMMARY_DAY",
    "DEFAULT_SUMMARY_HOUR",
    "DEFAULT_SUMMARY_MINUTE",
    "LAST_SUMMARY_FILE",
    "LOG_LEVEL_MAP",
    "POLL_OPTION_MAX_LENGTH",
    "POLL_QUESTION_MAX_LENGTH",
    "POLL_REGEN_THRESHOLD_DEFAULT",
    "POLL_REGENERATIONS_FILE",
    "POLL_PROMPT_FILE",
    "PROMPT_FILE",
    "RESTART_FLAG_FILE",
    "RETRY_BASE_DELAY",
    "RETRY_MAX_ATTEMPTS",
    "RETRY_MAX_DELAY",
    "SESSIONS_DIR",
    "VALID_BOT_STATES",
    "VALID_DAYS",
    "VALID_FREQUENCIES",
    "BOT_STATE_RUNNING",
    "BOT_STATE_PAUSED",
    "BOT_STATE_SHUTTING_DOWN",
    # Date utilities
    "extract_date_range_from_summary",
    # Exceptions
    "AIServiceError",
    "BotError",
    "ChannelNotFoundError",
    "ConfigurationError",
    "DatabaseError",
    "InvalidScheduleError",
    "PollGenerationError",
    "TelegramAPIError",
    "ValidationError",
    # Message utilities
    "format_schedule_info",
    "split_long_message",
    # States
    "UserContext",
    "get_user_context",
    # Version utilities
    "compare_versions",
    "get_local_version",
]

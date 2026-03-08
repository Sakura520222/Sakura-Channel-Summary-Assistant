# Telegram Integration Layer
"""
Telegram-specific functionality and client management.
"""

from .client import (
    extract_date_range_from_summary,
    fetch_last_week_messages,
    get_active_client,
    send_long_message,
    send_poll,
    send_poll_to_channel,
    send_poll_to_discussion_group,
    send_report,
    set_active_client,
)
from .client_utils import (
    sanitize_markdown,
    split_message_smart,
    validate_message_entities,
)

__all__ = [
    "extract_date_range_from_summary",
    "fetch_last_week_messages",
    "get_active_client",
    "sanitize_markdown",
    "send_long_message",
    "send_poll",
    "send_poll_to_channel",
    "send_poll_to_discussion_group",
    "send_report",
    "set_active_client",
    "split_message_smart",
    "validate_message_entities",
]

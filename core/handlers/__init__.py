# Handlers Layer: Request and message handlers
"""
Request and message handlers for processing incoming events.
"""

__all__ = [
    "CommentWelcomeHandler",
    "get_default_comment_welcome_config",
    "validate_callback_data_length",
    "MainBotPushHandler",
    "MainBotRequestHandler",
    "SubmissionHandler",
    "get_submission_handler",
    "SubmissionReviewHandler",
    "get_submission_review_handler",
    "UserBotClient",
    "get_userbot_client",
]

_EXPORTS = {
    "CommentWelcomeHandler": ("channel_comment_welcome", "CommentWelcomeHandler"),
    "get_default_comment_welcome_config": (
        "channel_comment_welcome_config",
        "get_default_comment_welcome_config",
    ),
    "validate_callback_data_length": (
        "channel_comment_welcome_config",
        "validate_callback_data_length",
    ),
    "MainBotPushHandler": ("mainbot_push_handler", "MainBotPushHandler"),
    "MainBotRequestHandler": ("mainbot_request_handler", "MainBotRequestHandler"),
    "SubmissionHandler": ("submission_handler", "SubmissionHandler"),
    "get_submission_handler": ("submission_handler", "get_submission_handler"),
    "SubmissionReviewHandler": ("submission_review_handler", "SubmissionReviewHandler"),
    "get_submission_review_handler": (
        "submission_review_handler",
        "get_submission_review_handler",
    ),
    "UserBotClient": ("userbot_client", "UserBotClient"),
    "get_userbot_client": ("userbot_client", "get_userbot_client"),
}


def __getattr__(name: str):
    """按需导入 handler，避免导入包时初始化所有业务依赖。"""
    if name in _EXPORTS:
        import importlib

        module_name, attr_name = _EXPORTS[name]
        module = importlib.import_module(f"{__name__}.{module_name}")
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

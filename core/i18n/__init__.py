# Internationalization (i18n)
"""
Internationalization and localization support.
"""

from .i18n import I18nManager, get_language, get_supported_languages, get_text, set_language, t

__all__ = [
    "I18nManager",
    "get_language",
    "get_supported_languages",
    "get_text",
    "set_language",
    "t",
]

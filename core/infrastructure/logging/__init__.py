# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""统一日志管理模块

提供统一的日志配置管理，支持控制台和文件输出，支持日志轮转。
"""

from .config import get_component_log_file_path, setup_component_logging, setup_logging
from .formatters import ColorFormatter, FileFormatter
from .handlers import SafeRotatingFileHandler

__all__ = [
    "setup_logging",
    "setup_component_logging",
    "get_component_log_file_path",
    "ColorFormatter",
    "FileFormatter",
    "SafeRotatingFileHandler",
]

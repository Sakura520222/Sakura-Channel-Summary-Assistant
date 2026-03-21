# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""自定义日志处理器

提供线程安全的日志处理器，支持日志轮转。
"""

import logging
import threading
from logging.handlers import RotatingFileHandler


class SafeRotatingFileHandler(RotatingFileHandler):
    """线程安全的轮转文件处理器

    继承自 RotatingFileHandler，增加线程安全保证。
    """

    def __init__(self, *args, **kwargs):
        """初始化处理器"""
        self._lock = threading.RLock()
        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord) -> None:
        """发出日志记录（线程安全）"""
        with self._lock:
            try:
                super().emit(record)
            except Exception:
                self.handleError(record)

    def doRollover(self) -> None:
        """执行日志轮转（线程安全）"""
        with self._lock:
            super().doRollover()


class ContextFilter(logging.Filter):
    """上下文过滤器

    可以添加额外的上下文信息到日志记录中。
    """

    def __init__(self, context: dict | None = None):
        """初始化过滤器

        Args:
            context: 要添加的上下文信息
        """
        super().__init__()
        self.context = context or {}

    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录

        Args:
            record: 日志记录

        Returns:
            是否记录该日志
        """
        # 添加上下文信息
        for key, value in self.context.items():
            setattr(record, key, value)
        return True

# core/infrastructure/exceptions.py
"""Sakura-Bot 自定义异常类

提供项目特定的异常类型，便于精确的错误处理和恢复。
"""


class SakuraBotError(Exception):
    """Sakura-Bot 基础异常

    所有项目特定异常的基类。
    """

    def __init__(self, message: str, details: dict | None = None):
        """初始化异常

        Args:
            message: 错误消息
            details: 额外的错误详情（可选）
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class DatabaseError(SakuraBotError):
    """数据库相关错误

    用于数据库连接、查询、迁移等操作失败的情况。
    """

    def __init__(
        self,
        message: str,
        db_type: str | None = None,
        operation: str | None = None,
        details: dict | None = None,
    ):
        """初始化数据库异常

        Args:
            message: 错误消息
            db_type: 数据库类型（如 "mysql"）
            operation: 操作类型（如 "connect", "query", "migrate"）
            details: 额外的错误详情
        """
        details = details or {}
        if db_type:
            details["db_type"] = db_type
        if operation:
            details["operation"] = operation
        super().__init__(message, details)


class ConfigError(SakuraBotError):
    """配置相关错误

    用于配置加载、验证、热重载等操作失败的情况。
    """

    def __init__(
        self,
        message: str,
        config_file: str | None = None,
        config_key: str | None = None,
        details: dict | None = None,
    ):
        """初始化配置异常

        Args:
            message: 错误消息
            config_file: 配置文件路径
            config_key: 配置键名
            details: 额外的错误详情
        """
        details = details or {}
        if config_file:
            details["config_file"] = config_file
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details)


class AIError(SakuraBotError):
    """AI 服务相关错误

    用于 AI API 调用、向量存储、嵌入生成等操作失败的情况。
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        model: str | None = None,
        details: dict | None = None,
    ):
        """初始化 AI 异常

        Args:
            message: 错误消息
            provider: AI 服务提供商（如 "openai", "anthropic"）
            model: 模型名称
            details: 额外的错误详情
        """
        details = details or {}
        if provider:
            details["provider"] = provider
        if model:
            details["model"] = model
        super().__init__(message, details)


class TelegramError(SakuraBotError):
    """Telegram 相关错误

    用于 Telegram API 调用、消息发送、文件处理等操作失败的情况。
    """

    def __init__(
        self,
        message: str,
        chat_id: str | int | None = None,
        operation: str | None = None,
        details: dict | None = None,
    ):
        """初始化 Telegram 异常

        Args:
            message: 错误消息
            chat_id: 聊天 ID
            operation: 操作类型（如 "send_message", "get_chat"）
            details: 额外的错误详情
        """
        details = details or {}
        if chat_id:
            details["chat_id"] = str(chat_id)
        if operation:
            details["operation"] = operation
        super().__init__(message, details)


class ValidationError(SakuraBotError):
    """数据验证错误

    用于输入验证、参数检查等失败的情况。
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: any = None,
        details: dict | None = None,
    ):
        """初始化验证异常

        Args:
            message: 错误消息
            field: 验证失败的字段名
            value: 验证失败的值
            details: 额外的错误详情
        """
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details)


class InitializationError(SakuraBotError):
    """初始化错误

    用于组件初始化失败的情况。
    """

    def __init__(
        self,
        message: str,
        component: str | None = None,
        details: dict | None = None,
    ):
        """初始化初始化异常

        Args:
            message: 错误消息
            component: 组件名称
            details: 额外的错误详情
        """
        details = details or {}
        if component:
            details["component"] = component
        super().__init__(message, details)

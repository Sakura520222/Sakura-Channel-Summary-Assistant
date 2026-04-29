# core/config/validator.py
import json
import logging
from pathlib import Path

from core.config.events import ConfigValidationErrorEvent

logger = logging.getLogger(__name__)


class ConfigValidator:
    """配置文件验证器（增强版）"""

    # 有效的日志级别
    VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    # 有效的频率值
    VALID_FREQUENCIES = {"daily", "weekly"}

    # 有效的星期几
    VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}

    @staticmethod
    def validate_config_file(
        file_path: Path,
    ) -> tuple[bool, ConfigValidationErrorEvent | None, dict | None]:
        """
        验证配置文件（JSON格式 + 业务逻辑）

        Returns:
            (成功, 错误事件, 配置字典)
        """
        try:
            if not file_path.exists():
                error_event = ConfigValidationErrorEvent(
                    error=f"配置文件不存在: {file_path}", config_path=str(file_path)
                )
                return False, error_event, None

            with open(file_path, encoding="utf-8") as f:
                config_dict = json.load(f)

            # 业务逻辑验证
            validation_error = ConfigValidator._validate_business_logic(config_dict, file_path)
            if validation_error:
                return False, validation_error, None

            return True, None, config_dict

        except json.JSONDecodeError as e:
            # JSON解析错误，提取行号和列号
            error_event = ConfigValidationErrorEvent(
                error=f"JSON格式错误: {e.msg}",
                config_path=str(file_path),
                error_line=e.lineno,
                error_column=e.colno,
            )
            return False, error_event, None

        except Exception as e:
            error_event = ConfigValidationErrorEvent(
                error=f"未知错误: {str(e)}", config_path=str(file_path)
            )
            return False, error_event, None

    @staticmethod
    def _validate_business_logic(
        config: dict, file_path: Path
    ) -> ConfigValidationErrorEvent | None:
        """验证配置的业务逻辑"""

        # 1. 验证 log_level
        if "log_level" in config:
            log_level = config["log_level"]
            if (
                not isinstance(log_level, str)
                or log_level.upper() not in ConfigValidator.VALID_LOG_LEVELS
            ):
                return ConfigValidationErrorEvent(
                    error=f"无效的日志级别: {log_level}，有效值: {', '.join(ConfigValidator.VALID_LOG_LEVELS)}",
                    config_path=str(file_path),
                )

        # 2. 验证 summary_schedules
        if "summary_schedules" in config:
            schedules = config["summary_schedules"]
            if not isinstance(schedules, dict):
                return ConfigValidationErrorEvent(
                    error="summary_schedules 必须是对象类型", config_path=str(file_path)
                )

            for channel, schedule in schedules.items():
                error = ConfigValidator._validate_schedule(schedule, channel, file_path)
                if error:
                    return error

        # 3. 验证 channel_poll_settings
        if "channel_poll_settings" in config:
            poll_settings = config["channel_poll_settings"]
            if not isinstance(poll_settings, dict):
                return ConfigValidationErrorEvent(
                    error="channel_poll_settings 必须是对象类型", config_path=str(file_path)
                )

        # 4. 验证 forwarding 配置
        if "forwarding" in config:
            forwarding = config["forwarding"]
            if not isinstance(forwarding, dict):
                return ConfigValidationErrorEvent(
                    error="forwarding 必须是对象类型", config_path=str(file_path)
                )

        # 5. 验证 channel_auto_poll_settings
        if "channel_auto_poll_settings" in config:
            auto_poll_settings = config["channel_auto_poll_settings"]
            if not isinstance(auto_poll_settings, dict):
                return ConfigValidationErrorEvent(
                    error="channel_auto_poll_settings 必须是对象类型", config_path=str(file_path)
                )

        return None

    @staticmethod
    def _validate_schedule(
        schedule: dict, channel: str, file_path: Path
    ) -> ConfigValidationErrorEvent | None:
        """验证单个时间配置"""
        if not isinstance(schedule, dict):
            return ConfigValidationErrorEvent(
                error=f"频道 {channel} 的时间配置必须是对象类型", config_path=str(file_path)
            )

        # 验证 frequency
        frequency = schedule.get("frequency")
        if frequency and frequency not in ConfigValidator.VALID_FREQUENCIES:
            return ConfigValidationErrorEvent(
                error=f"无效的频率: {frequency}，有效值: {', '.join(ConfigValidator.VALID_FREQUENCIES)}",
                config_path=str(file_path),
            )

        # 验证时间范围
        hour = schedule.get("hour")
        if hour is not None and (not isinstance(hour, int) or hour < 0 or hour > 23):
            return ConfigValidationErrorEvent(
                error=f"无效的小时: {hour}，有效范围: 0-23", config_path=str(file_path)
            )

        minute = schedule.get("minute")
        if minute is not None and (not isinstance(minute, int) or minute < 0 or minute > 59):
            return ConfigValidationErrorEvent(
                error=f"无效的分钟: {minute}，有效范围: 0-59", config_path=str(file_path)
            )

        return None

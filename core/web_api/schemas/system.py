# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""
系统运维相关的请求/响应模型
"""

from pydantic import BaseModel, Field, field_validator


class BotStatusResponse(BaseModel):
    """Bot 状态响应"""

    status: str = Field(..., description="Bot 运行状态: running / paused / shutting_down")
    version: str = Field(default="unknown", description="Bot 版本")
    log_level: str = Field(default="INFO", description="当前日志级别")
    channel_count: int = Field(default=0, description="监控频道数量")
    forwarding_enabled: bool = Field(default=False, description="转发功能是否启用")
    qa_bot_running: bool = Field(default=False, description="QA Bot 是否运行中")
    userbot_connected: bool = Field(default=False, description="UserBot 是否连接")
    uptime_seconds: float = Field(default=0, description="运行时长（秒）")


class LogLevelUpdate(BaseModel):
    """日志级别更新请求"""

    level: str = Field(..., description="新的日志级别")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"无效的日志级别: {v}，可选: {', '.join(valid_levels)}")
        return v_upper

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
定时任务相关的请求/响应模型
"""

from pydantic import BaseModel, Field, field_validator


class ScheduleInfo(BaseModel):
    """定时任务信息"""

    channel: str = Field(..., description="频道 URL")
    frequency: str = Field(..., description="频率: daily / weekly")
    hour: int = Field(default=9, description="小时 (0-23)")
    minute: int = Field(default=0, description="分钟 (0-59)")
    days: list[str] = Field(default_factory=list, description="星期列表（仅 weekly）")

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        if v not in ("daily", "weekly"):
            raise ValueError("频率必须为 daily 或 weekly")
        return v

    @field_validator("hour")
    @classmethod
    def validate_hour(cls, v: int) -> int:
        if not 0 <= v <= 23:
            raise ValueError("小时必须在 0-23 之间")
        return v

    @field_validator("minute")
    @classmethod
    def validate_minute(cls, v: int) -> int:
        if not 0 <= v <= 59:
            raise ValueError("分钟必须在 0-59 之间")
        return v


class ScheduleUpdateRequest(BaseModel):
    """更新定时任务请求"""

    frequency: str = Field(..., description="频率: daily / weekly")
    hour: int = Field(default=9, description="小时 (0-23)")
    minute: int = Field(default=0, description="分钟 (0-59)")
    days: list[str] = Field(default_factory=lambda: ["mon"], description="星期列表")

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        if v not in ("daily", "weekly"):
            raise ValueError("频率必须为 daily 或 weekly")
        return v


class LastSummaryTimeUpdateRequest(BaseModel):
    """上次总结时间更新请求"""

    time: str = Field(..., description="ISO 8601 时间字符串")
    summary_message_ids: list[int] = Field(default_factory=list, description="总结消息 ID 列表")
    poll_message_ids: list[int] = Field(default_factory=list, description="投票消息 ID 列表")
    button_message_ids: list[int] = Field(default_factory=list, description="按钮消息 ID 列表")

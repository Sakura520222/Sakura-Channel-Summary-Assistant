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
频道管理相关的请求/响应模型
"""

from pydantic import BaseModel, Field


class ChannelAddRequest(BaseModel):
    """添加频道请求"""

    channel_url: str = Field(..., description="频道 URL（如 https://t.me/channel_name）")


class ChannelDeleteRequest(BaseModel):
    """删除频道请求"""

    channel_url: str = Field(..., description="要删除的频道 URL")


class ChannelInfo(BaseModel):
    """频道信息"""

    url: str = Field(..., description="频道 URL")
    has_schedule: bool = Field(default=False, description="是否配置了定时任务")
    has_poll_settings: bool = Field(default=False, description="是否配置了投票设置")


class ChannelListResponse(BaseModel):
    """频道列表响应"""

    channels: list[ChannelInfo] = Field(default_factory=list, description="频道列表")
    total: int = Field(default=0, description="频道总数")


class ApiResponse(BaseModel):
    """通用 API 响应"""

    success: bool = Field(..., description="操作是否成功")
    message: str = Field(default="", description="响应消息")
    data: dict | list | None = Field(default=None, description="响应数据")

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
统计数据相关的请求/响应模型
"""

from pydantic import BaseModel, Field


class StatsResponse(BaseModel):
    """统计信息响应"""

    total_channels: int = Field(default=0, description="频道总数")
    total_summaries: int = Field(default=0, description="总结总数")
    total_forwarded: int = Field(default=0, description="转发消息总数")
    bot_status: str = Field(default="running", description="Bot 运行状态")
    uptime: str = Field(default="unknown", description="运行时长")


class SummaryItem(BaseModel):
    """总结条目"""

    id: int | None = Field(default=None, description="总结 ID")
    channel: str = Field(default="", description="频道标识")
    summary_text: str = Field(default="", description="总结内容")
    message_count: int = Field(default=0, description="消息数量")
    created_at: str = Field(default="", description="创建时间")


class SummaryListResponse(BaseModel):
    """总结列表响应"""

    summaries: list[SummaryItem] = Field(default_factory=list, description="总结列表")
    total: int = Field(default=0, description="总结总数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")


class ChannelRankingItem(BaseModel):
    """频道排名条目"""

    channel: str = Field(..., description="频道标识")
    summary_count: int = Field(default=0, description="总结数量")
    message_count: int = Field(default=0, description="消息总数")

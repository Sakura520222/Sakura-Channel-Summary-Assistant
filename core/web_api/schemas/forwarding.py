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
转发规则相关的请求/响应模型
"""

from pydantic import BaseModel, Field


class ForwardingRuleBase(BaseModel):
    """转发规则基础字段"""

    source_channel: str = Field(..., description="源频道 URL")
    target_channel: str = Field(..., description="目标频道 URL")
    keywords: list[str] = Field(default_factory=list, description="关键词过滤列表")
    blacklist: list[str] = Field(default_factory=list, description="黑名单列表")
    patterns: list[str] = Field(default_factory=list, description="正则过滤模式列表")
    blacklist_patterns: list[str] = Field(default_factory=list, description="正则黑名单模式列表")
    copy_mode: bool = Field(default=False, description="是否使用复制模式")
    forward_original_only: bool = Field(default=False, description="是否只转发原始消息")
    custom_footer: str = Field(default="", description="自定义页脚文本")


class ForwardingRuleCreate(ForwardingRuleBase):
    """创建转发规则请求"""

    pass


class ForwardingRuleUpdate(ForwardingRuleBase):
    """更新转发规则请求"""

    pass


class ForwardingToggleRequest(BaseModel):
    """转发开关请求"""

    enabled: bool = Field(..., description="是否启用转发")


class ForwardingConfigResponse(BaseModel):
    """转发配置响应"""

    enabled: bool = Field(default=False, description="是否启用转发")
    show_default_footer: bool = Field(default=True, description="是否显示默认页脚")
    rules: list[dict] = Field(default_factory=list, description="转发规则列表")
    rule_count: int = Field(default=0, description="规则数量")

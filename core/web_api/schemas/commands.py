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
命令中心相关的请求/响应模型
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

CommandRisk = Literal["safe", "normal", "danger"]
ParameterType = Literal["string", "number", "boolean", "select", "tags", "textarea"]
CommandResultData = dict[str, Any]


class CommandParameter(BaseModel):
    """命令参数定义"""

    name: str = Field(..., description="参数名")
    label: str = Field(..., description="显示名称")
    type: ParameterType = Field(default="string", description="参数类型")
    required: bool = Field(default=False, description="是否必填")
    description: str = Field(default="", description="参数说明")
    placeholder: str = Field(default="", description="输入占位符")
    default: Any | None = Field(default=None, description="默认值")
    options: list[dict[str, Any]] = Field(default_factory=list, description="可选项")


class CommandItem(BaseModel):
    """命令中心命令项"""

    command: str = Field(..., description="Telegram 命令名")
    description: str = Field(..., description="命令说明")
    operation_id: str = Field(..., description="WebUI 操作 ID")
    category: str = Field(..., description="分类名称")
    risk: CommandRisk = Field(default="normal", description="风险等级")
    executable: bool = Field(default=True, description="是否可在 WebUI 执行")
    covered_by_page: str | None = Field(default=None, description="已覆盖该能力的页面")
    parameters: list[CommandParameter] = Field(default_factory=list, description="参数定义")
    aliases: list[str] = Field(default_factory=list, description="命令别名")


class CommandCategory(BaseModel):
    """命令分类"""

    category: str = Field(..., description="分类名称")
    i18n_key: str = Field(default="", description="国际化键名")
    commands: list[CommandItem] = Field(default_factory=list, description="命令列表")


class CommandExecuteRequest(BaseModel):
    """命令执行请求"""

    params: dict[str, Any] = Field(default_factory=dict, description="结构化参数")
    confirm: bool = Field(default=False, description="是否已二次确认")
    confirm_text: str = Field(default="", description="确认文本")


class CommandExecuteResponse(BaseModel):
    """命令执行响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="结果消息")
    data: CommandResultData = Field(default_factory=dict, description="结果数据")

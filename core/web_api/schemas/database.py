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
数据库管理相关的请求/响应模型
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class RowDataRequestBase(BaseModel):
    """行数据请求基类"""

    data: dict[str, Any] = Field(..., description="列名→值的字典")

    @field_validator("data")
    @classmethod
    def validate_data_not_empty(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not v:
            raise ValueError("data 不能为空")
        return v


class RowCreateRequest(RowDataRequestBase):
    """创建行请求"""


class RowUpdateRequest(RowDataRequestBase):
    """更新行请求"""

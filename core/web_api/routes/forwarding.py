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
转发规则 API 路由

提供转发功能的启用/禁用、规则增删改查功能。
"""

import logging

from fastapi import APIRouter, HTTPException

from core.config import normalize_channel_id
from core.web_api.deps import get_config, write_config
from core.web_api.schemas.forwarding import (
    ForwardingConfigResponse,
    ForwardingRuleCreate,
    ForwardingRuleUpdate,
    ForwardingToggleRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_forwarding_config():
    """获取转发配置和所有规则"""
    try:
        config = get_config()
        fwd = config.get("forwarding", {})

        return {
            "success": True,
            "data": ForwardingConfigResponse(
                enabled=fwd.get("enabled", False),
                show_default_footer=fwd.get("show_default_footer", True),
                rules=fwd.get("rules", []),
                rule_count=len(fwd.get("rules", [])),
            ).model_dump(),
        }

    except Exception as e:
        logger.error(f"获取转发配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/enabled")
async def toggle_forwarding(request: ForwardingToggleRequest):
    """启用/禁用转发功能"""
    try:
        config = get_config()
        if "forwarding" not in config:
            config["forwarding"] = {}

        config["forwarding"]["enabled"] = request.enabled
        write_config(config)

        status_text = "启用" if request.enabled else "禁用"
        logger.info(f"已通过 WebUI {status_text}转发功能")
        return {"success": True, "message": f"转发功能已{status_text}"}

    except Exception as e:
        logger.error(f"切换转发状态失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/footer")
async def update_footer_config(request: dict):
    """更新页脚配置"""
    try:
        config = get_config()
        if "forwarding" not in config:
            config["forwarding"] = {}

        if "show_default_footer" in request:
            config["forwarding"]["show_default_footer"] = request["show_default_footer"]

        write_config(config)
        return {"success": True, "message": "页脚配置已更新"}

    except Exception as e:
        logger.error(f"更新页脚配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/rules")
async def add_rule(request: ForwardingRuleCreate):
    """添加转发规则"""
    try:
        source = normalize_channel_id(request.source_channel)
        target = normalize_channel_id(request.target_channel)

        if not source or not target:
            return {"success": False, "message": "无效的源频道或目标频道 URL"}

        config = get_config()
        if "forwarding" not in config:
            config["forwarding"] = {}

        rules = config["forwarding"].get("rules", [])

        # 检查重复规则
        for rule in rules:
            if rule.get("source_channel") == source and rule.get("target_channel") == target:
                return {"success": False, "message": "该转发规则已存在"}

        new_rule = {
            "source_channel": source,
            "target_channel": target,
            "keywords": request.keywords,
            "blacklist": request.blacklist,
            "patterns": request.patterns,
            "blacklist_patterns": request.blacklist_patterns,
            "copy_mode": request.copy_mode,
            "forward_original_only": request.forward_original_only,
        }
        if request.custom_footer:
            new_rule["custom_footer"] = request.custom_footer

        rules.append(new_rule)
        config["forwarding"]["rules"] = rules
        write_config(config)

        logger.info(f"已通过 WebUI 添加转发规则: {source} -> {target}")
        return {"success": True, "message": f"转发规则已添加: {source} -> {target}"}

    except Exception as e:
        logger.error(f"添加转发规则失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/rules/{rule_index}")
async def update_rule(rule_index: int, request: ForwardingRuleUpdate):
    """更新指定索引的转发规则"""
    try:
        config = get_config()
        rules = config.get("forwarding", {}).get("rules", [])

        if rule_index < 0 or rule_index >= len(rules):
            return {"success": False, "message": f"无效的规则索引: {rule_index}"}

        source = normalize_channel_id(request.source_channel)
        target = normalize_channel_id(request.target_channel)

        rules[rule_index] = {
            "source_channel": source,
            "target_channel": target,
            "keywords": request.keywords,
            "blacklist": request.blacklist,
            "patterns": request.patterns,
            "blacklist_patterns": request.blacklist_patterns,
            "copy_mode": request.copy_mode,
            "forward_original_only": request.forward_original_only,
        }
        if request.custom_footer:
            rules[rule_index]["custom_footer"] = request.custom_footer

        config["forwarding"]["rules"] = rules
        write_config(config)

        logger.info(f"已通过 WebUI 更新转发规则 #{rule_index}")
        return {"success": True, "message": f"转发规则已更新: #{rule_index}"}

    except Exception as e:
        logger.error(f"更新转发规则失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/rules/{rule_index}")
async def delete_rule(rule_index: int):
    """删除指定索引的转发规则"""
    try:
        config = get_config()
        rules = config.get("forwarding", {}).get("rules", [])

        if rule_index < 0 or rule_index >= len(rules):
            return {"success": False, "message": f"无效的规则索引: {rule_index}"}

        removed = rules.pop(rule_index)
        config["forwarding"]["rules"] = rules
        write_config(config)

        source = removed.get("source_channel", "?")
        target = removed.get("target_channel", "?")
        logger.info(f"已通过 WebUI 删除转发规则: {source} -> {target}")
        return {"success": True, "message": f"转发规则已删除: {source} -> {target}"}

    except Exception as e:
        logger.error(f"删除转发规则失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e

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
频道消息转发命令处理器

提供转发功能的命令接口：
- /forwarding 查看转发状态
- /forwarding_enable 启用转发
- /forwarding_disable 禁用转发
- /forwarding_stats 查看转发统计
"""

import logging
from typing import TYPE_CHECKING

from core.i18n.i18n import get_text as t

if TYPE_CHECKING:
    from telethon import TelegramClient
    from telethon.tl.types import Message

    from core.forwarding.forwarding_handler import ForwardingHandler

logger = logging.getLogger(__name__)


async def cmd_forwarding_status(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    查看转发状态

    用法: /forwarding
    """
    try:
        status_text = (
            t("forwarding.status_enabled") if handler.enabled else t("forwarding.status_disabled")
        )
        rule_count = len(handler.config.get("rules", []))

        response = t(
            "forwarding.status_message",
            status=status_text,
            rule_count=rule_count,
        )

        # 如果有规则，列出规则
        if rule_count > 0:
            response += "\n\n" + t("forwarding.rules_header")
            for i, rule in enumerate(handler.config.get("rules", []), 1):
                source = rule.get("source_channel", "Unknown")
                target = rule.get("target_channel", "Unknown")
                response += f"\n{i}. {source} → {target}"

        await message.reply(response)
        logger.info(f"用户 {message.sender_id} 查询转发状态")

    except Exception as e:
        logger.error(f"查询转发状态失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(t("forwarding.error.query_failed", error=str(e)))


async def cmd_forwarding_enable(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    启用转发功能（持久化到配置文件）

    用法: /forwarding_enable
    """
    try:
        if handler.enabled:
            await message.reply(t("forwarding.already_enabled"))
            return

        # 更新内存状态
        handler.enabled = True

        # 持久化到配置文件
        from core.config import load_config, save_config

        config = load_config()
        if "forwarding" not in config:
            config["forwarding"] = {}
        config["forwarding"]["enabled"] = True
        save_config(config)

        await message.reply(t("forwarding.enabled"))
        logger.info(f"用户 {message.sender_id} 启用了转发功能（已保存到配置文件）")

    except Exception as e:
        logger.error(f"启用转发功能失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(t("forwarding.error.enable_failed", error=str(e)))


async def cmd_forwarding_disable(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    禁用转发功能（持久化到配置文件）

    用法: /forwarding_disable
    """
    try:
        if not handler.enabled:
            await message.reply(t("forwarding.already_disabled"))
            return

        # 更新内存状态
        handler.enabled = False

        # 持久化到配置文件
        from core.config import load_config, save_config

        config = load_config()
        if "forwarding" not in config:
            config["forwarding"] = {}
        config["forwarding"]["enabled"] = False
        save_config(config)

        await message.reply(t("forwarding.disabled"))
        logger.info(f"用户 {message.sender_id} 禁用了转发功能（已保存到配置文件）")

    except Exception as e:
        logger.error(f"禁用转发功能失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(t("forwarding.error.disable_failed", error=str(e)))


async def cmd_forwarding_stats(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    查看转发统计

    用法: /forwarding_stats [频道URL]
    """
    try:
        # 解析参数
        args = message.message.split()[1:] if message.message else []
        channel_id = args[0] if args else None

        stats = await handler.get_statistics(channel_id)

        if not stats:
            await message.reply(t("forwarding.stats.no_data"))
            return

        # 格式化统计信息
        if channel_id:
            # 单个频道统计
            response = t(
                "forwarding.stats.single_channel",
                channel=channel_id,
                total=stats.get("total_forwarded", 0),
                last=stats.get("last_forwarded") or t("forwarding.stats.never"),
            )
        else:
            # 所有频道统计
            total_all = stats.get("total_all_channels", 0)
            response = t("forwarding.stats.total", total=total_all)

            # 列出各频道统计
            by_channel = stats.get("by_channel", [])
            if by_channel:
                response += "\n\n" + t("forwarding.stats.by_channel_header")
                for item in by_channel[:10]:  # 最多显示10个
                    channel = item.get("channel_id", "Unknown")
                    count = item.get("total_forwarded", 0)
                    response += f"\n• {channel}: {count}"

        await message.reply(response)
        logger.info(f"用户 {message.sender_id} 查询转发统计")

    except Exception as e:
        logger.error(f"查询转发统计失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(t("forwarding.error.stats_failed", error=str(e)))


async def cmd_forwarding_footer(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    设置或清除自定义底栏

    用法:
    /forwarding_footer <源频道> <目标频道> <底栏内容>
    /forwarding_footer <源频道> <目标频道> clear

    支持的占位符:
    - {source_link}: 源消息链接
    - {source_title}: 源频道名称
    - {target_title}: 目标频道名称
    - {source_channel}: 源频道ID
    - {target_channel}: 目标频道ID
    - {message_id}: 消息ID

    示例:
    /forwarding_footer https://t.me/source https://t.me/target 📢 来源: {source_title}\\n🔗 {source_link}
    /forwarding_footer https://t.me/source https://t.me/target clear
    """
    try:
        # 解析参数
        args = message.message.split()[1:] if message.message else []

        if len(args) < 2:
            await message.reply(t("forwarding.footer.usage"))
            return

        source_channel = args[0]
        target_channel = args[1]

        # 查找匹配的转发规则
        config = handler.config
        rules = config.get("rules", [])
        matched_rule = None

        for rule in rules:
            if (
                rule.get("source_channel", "").rstrip("/").split("/")[-1]
                == source_channel.rstrip("/").split("/")[-1]
                and rule.get("target_channel", "").rstrip("/").split("/")[-1]
                == target_channel.rstrip("/").split("/")[-1]
            ):
                matched_rule = rule
                break

        if not matched_rule:
            await message.reply(
                t("forwarding.footer.not_found", source=source_channel, target=target_channel)
            )
            return

        # 检查是否要清除底栏
        if len(args) >= 3 and args[2].lower() == "clear":
            matched_rule["custom_footer"] = ""
            await message.reply(
                t(
                    "forwarding.footer.cleared",
                    source=source_channel,
                    target=target_channel,
                )
            )
            logger.info(f"用户 {message.sender_id} 清除了转发规则底栏")
            return

        # 设置自定义底栏
        if len(args) < 3:
            await message.reply(t("forwarding.footer.invalid_params"))
            return

        # 获取底栏内容（可能包含空格，所以需要特殊处理）
        footer_text = " ".join(args[2:])

        # 存储到配置中
        matched_rule["custom_footer"] = footer_text

        await message.reply(
            t(
                "forwarding.footer.updated",
                source=source_channel,
                target=target_channel,
                footer=footer_text,
            )
        )
        logger.info(
            f"用户 {message.sender_id} 更新了转发规则底栏: {source_channel} -> {target_channel}"
        )

    except Exception as e:
        logger.error(f"设置底栏失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(t("forwarding.error.query_failed", error=str(e)))


async def cmd_forwarding_default_footer(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    启用或禁用默认底栏

    用法:
    /forwarding_default_footer on - 启用默认底栏
    /forwarding_default_footer off - 禁用默认底栏

    说明:
    - 启用：未设置自定义底栏的转发规则将使用默认格式
    - 禁用：所有转发规则都不会添加底栏（包括自定义底栏）
    """
    try:
        # 解析参数
        args = message.message.split()[1:] if message.message else []

        if not args:
            await message.reply(t("forwarding.default_footer.usage"))
            return

        action = args[0].lower()

        # 更新全局配置
        config = handler.config

        if action in ["on", "true", "1", "yes"]:
            config["show_default_footer"] = True
            await message.reply(t("forwarding.footer.default_enabled"))
            logger.info(f"用户 {message.sender_id} 启用了默认底栏")
        elif action in ["off", "false", "0", "no"]:
            config["show_default_footer"] = False
            await message.reply(t("forwarding.footer.default_disabled"))
            logger.info(f"用户 {message.sender_id} 禁用了默认底栏")
        else:
            await message.reply(t("forwarding.default_footer.usage"))

    except Exception as e:
        logger.error(f"设置默认底栏失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(t("forwarding.error.query_failed", error=str(e)))


async def cmd_forwarding_add_rule(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    添加转发规则（持久化到配置文件）

    用法: /forwarding_add_rule <源频道> <目标频道>

    示例: /forwarding_add_rule https://t.me/source https://t.me/target
    """
    try:
        # 解析参数
        args = message.message.split()[1:] if message.message else []

        if len(args) < 2:
            await message.reply(
                "❌ 参数错误\n\n"
                "用法: /forwarding_add_rule <源频道> <目标频道>\n"
                "示例: /forwarding_add_rule https://t.me/source https://t.me/target"
            )
            return

        source_channel = args[0]
        target_channel = args[1]

        # 加载当前配置
        from core.config import load_config, save_config

        config = load_config()

        # 确保 forwarding 配置存在
        if "forwarding" not in config:
            config["forwarding"] = {"enabled": False, "rules": []}

        if "rules" not in config["forwarding"]:
            config["forwarding"]["rules"] = []

        # 检查规则是否已存在
        for rule in config["forwarding"]["rules"]:
            if (
                rule.get("source_channel", "").rstrip("/").split("/")[-1]
                == source_channel.rstrip("/").split("/")[-1]
                and rule.get("target_channel", "").rstrip("/").split("/")[-1]
                == target_channel.rstrip("/").split("/")[-1]
            ):
                await message.reply(f"⚠️ 转发规则已存在:\n{source_channel} → {target_channel}")
                return

        # 添加新规则
        new_rule = {
            "source_channel": source_channel,
            "target_channel": target_channel,
        }
        config["forwarding"]["rules"].append(new_rule)

        # 保存配置
        save_config(config)

        # 更新 handler 的配置
        handler.set_config(config["forwarding"])

        await message.reply(
            f"✅ 转发规则已添加:\n{source_channel} → {target_channel}\n\n"
            f"当前共有 {len(config['forwarding']['rules'])} 条规则\n"
            f"使用 /forwarding_enable 启用转发功能"
        )
        logger.info(f"用户 {message.sender_id} 添加了转发规则: {source_channel} → {target_channel}")

    except Exception as e:
        logger.error(f"添加转发规则失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(f"❌ 添加转发规则失败: {str(e)}")


async def cmd_forwarding_add_and_enable(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    一键添加转发规则并启用（持久化到配置文件）

    用法: /forwarding <源频道> <目标频道>

    示例: /forwarding https://t.me/source https://t.me/target
    """
    try:
        # 解析参数
        args = message.message.split()[1:] if message.message else []

        if len(args) < 2:
            # 没有参数，显示状态
            return await cmd_forwarding_status(client, message, handler)

        source_channel = args[0]
        target_channel = args[1]

        # 加载当前配置
        from core.config import load_config, save_config

        config = load_config()

        # 确保 forwarding 配置存在
        if "forwarding" not in config:
            config["forwarding"] = {"enabled": True, "rules": []}

        if "rules" not in config["forwarding"]:
            config["forwarding"]["rules"] = []

        # 检查规则是否已存在
        rule_exists = False
        for rule in config["forwarding"]["rules"]:
            if (
                rule.get("source_channel", "").rstrip("/").split("/")[-1]
                == source_channel.rstrip("/").split("/")[-1]
                and rule.get("target_channel", "").rstrip("/").split("/")[-1]
                == target_channel.rstrip("/").split("/")[-1]
            ):
                rule_exists = True
                break

        if not rule_exists:
            # 添加新规则
            new_rule = {
                "source_channel": source_channel,
                "target_channel": target_channel,
            }
            config["forwarding"]["rules"].append(new_rule)

        # 启用转发
        config["forwarding"]["enabled"] = True

        # 保存配置
        save_config(config)

        # 更新 handler 的配置和状态
        handler.set_config(config["forwarding"])
        handler.enabled = True

        if rule_exists:
            response = f"✅ 转发规则已存在，已启用转发:\n{source_channel} → {target_channel}"
        else:
            response = f"✅ 转发规则已添加并启用:\n{source_channel} → {target_channel}"

        response += f"\n\n当前共有 {len(config['forwarding']['rules'])} 条规则"
        await message.reply(response)
        logger.info(
            f"用户 {message.sender_id} 添加并启用了转发规则: {source_channel} → {target_channel}"
        )

    except Exception as e:
        logger.error(f"添加并启用转发规则失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(f"❌ 操作失败: {str(e)}")


async def cmd_forwarding_remove_rule(
    client: "TelegramClient", message: "Message", handler: "ForwardingHandler"
):
    """
    删除转发规则（持久化到配置文件）

    用法: /forwarding_remove_rule <源频道> <目标频道>

    示例: /forwarding_remove_rule https://t.me/source https://t.me/target
    """
    try:
        # 解析参数
        args = message.message.split()[1:] if message.message else []

        if len(args) < 2:
            await message.reply(
                "❌ 参数错误\n\n"
                "用法: /forwarding_remove_rule <源频道> <目标频道>\n"
                "示例: /forwarding_remove_rule https://t.me/source https://t.me/target"
            )
            return

        source_channel = args[0]
        target_channel = args[1]

        # 加载当前配置
        from core.config import load_config, save_config

        config = load_config()

        if "forwarding" not in config or "rules" not in config["forwarding"]:
            await message.reply("⚠️ 当前没有转发规则")
            return

        # 查找并删除规则
        original_count = len(config["forwarding"]["rules"])
        config["forwarding"]["rules"] = [
            rule
            for rule in config["forwarding"]["rules"]
            if not (
                rule.get("source_channel", "").rstrip("/").split("/")[-1]
                == source_channel.rstrip("/").split("/")[-1]
                and rule.get("target_channel", "").rstrip("/").split("/")[-1]
                == target_channel.rstrip("/").split("/")[-1]
            )
        ]

        if len(config["forwarding"]["rules"]) == original_count:
            await message.reply(f"⚠️ 未找到转发规则:\n{source_channel} → {target_channel}")
            return

        # 保存配置
        save_config(config)

        # 更新 handler 的配置
        handler.set_config(config["forwarding"])

        await message.reply(
            f"✅ 转发规则已删除:\n{source_channel} → {target_channel}\n\n"
            f"当前共有 {len(config['forwarding']['rules'])} 条规则"
        )
        logger.info(f"用户 {message.sender_id} 删除了转发规则: {source_channel} → {target_channel}")

    except Exception as e:
        logger.error(f"删除转发规则失败: {type(e).__name__}: {e}", exc_info=True)
        await message.reply(f"❌ 删除转发规则失败: {str(e)}")

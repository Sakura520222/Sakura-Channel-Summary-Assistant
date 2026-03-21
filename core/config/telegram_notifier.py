# core/config/telegram_notifier.py
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from telegram import Bot

from core.config.events import ConfigChangedEvent, ConfigValidationErrorEvent

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ConfigErrorNotifier:
    """配置通知器 - 支持错误和变更通知"""

    def __init__(self, bot_token: str, admin_chat_id: str):
        self._bot_token = bot_token
        self._admin_chat_id = admin_chat_id

    async def on_config_validation_error(self, event: ConfigValidationErrorEvent):
        """处理配置验证失败事件（支持回滚通知）"""
        try:
            bot = Bot(token=self._bot_token)

            # 构建增强的错误消息
            if event.rolled_back:
                message = f"""🚨 *配置验证失败并已自动回滚*

{event.format_error_message()}

🔄 *回滚操作*：配置已自动恢复到最后有效版本
📝 *建议*：请检查并修复配置文件中的 JSON 语法错误后保存，系统将自动重新加载"""
            else:
                message = f"""🚨 *配置验证失败*

{event.format_error_message()}

⚠️ *警告*：配置回滚失败，系统仍使用旧配置运行
📝 *建议*：请立即检查并手动修复配置文件"""

            await bot.send_message(
                chat_id=self._admin_chat_id,
                text=message,
                parse_mode="Markdown",
            )

            logger.info("已发送配置回滚通知到Telegram")

        except Exception as e:
            logger.error(f"发送Telegram回滚通知失败: {e}", exc_info=True)

    async def on_config_changed(self, event: ConfigChangedEvent):
        """处理配置变更成功事件 - 发送 Telegram 通知"""
        try:
            bot = Bot(token=self._bot_token)

            # 按配置分组
            grouped = self._group_changes(event.changed_fields) if event.changed_fields else {}

            # 构建消息
            message = f"""✅ *配置重载成功*

📊 版本: `{event.version}`
🕐 时间: {datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d %H:%M:%S")}
📝 变更字段: {len(event.changed_fields) if event.changed_fields else 0}个

{self._format_grouped_changes(grouped)}

💡 提示: 部分配置可能需要重启相关功能才能完全生效"""

            await bot.send_message(
                chat_id=self._admin_chat_id,
                text=message,
                parse_mode="Markdown",
            )

            logger.info("已发送配置重载成功通知到Telegram")

        except Exception as e:
            logger.error(f"发送配置变更通知失败: {e}", exc_info=True)

    def _group_changes(self, changed_fields: set[str]) -> dict:
        """将变更字段按配置区域分组"""
        sections = {
            "系统": {"channels", "log_level", "language", "send_report_to_source"},
            "投票": {
                "enable_poll",
                "poll_regen_threshold",
                "enable_vote_regen_request",
                "channel_poll_settings",
            },
            "转发": {"forwarding"},
            "总结": {"summary_schedules"},
            "评论欢迎": {"comment_welcome", "channel_comment_welcome"},
        }

        grouped = {}
        for field in changed_fields:
            top_level = field.split(".")[0]
            found = False
            for section, fields in sections.items():
                if top_level in fields:
                    grouped.setdefault(section, []).append(field)
                    found = True
                    break
            if not found:
                grouped.setdefault("其他", []).append(field)

        return grouped

    def _format_grouped_changes(self, grouped: dict) -> str:
        """格式化分组变更信息"""
        if not grouped:
            return "📋 无具体变更信息"

        lines = []
        for section, fields in grouped.items():
            lines.append(f"\n📌 *{section}配置*:")
            for field in fields[:5]:  # 最多显示5个字段
                lines.append(f"  • `{field}`")
            if len(fields) > 5:
                lines.append(f"  • ... 等 {len(fields)} 个字段")

        return "\n".join(lines)

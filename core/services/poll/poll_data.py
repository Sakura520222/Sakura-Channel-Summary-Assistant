# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""投票数据管理模块

此模块使用主 MySQL 数据库管理投票重新生成数据，提供高性能的异步访问。
"""

import asyncio
import logging

from core.infrastructure.utils.constants import CLEANUP_DAYS_DEFAULT
from core.infrastructure.utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


# 投票重新生成记录类型
PollRegenerationRecord = dict[
    str,  # 'channel', 'summary_msg_id', 'poll_msg_id', 'button_msg_id',
    # 'summary_text', 'channel_name', 'timestamp', 'send_to_channel',
    # 'vote_count', 'voters', 'discussion_forward_msg_id'
    str | int | bool | list[int] | None,
]


class PollRegenerationManager:
    """投票重新生成数据管理器

    使用主 MySQL 数据库管理投票重新生成数据，支持高并发访问。
    """

    def __init__(self, db_manager=None):
        """初始化数据管理器

        Args:
            db_manager: 数据库管理器实例，如果为None则获取全局实例
        """
        if db_manager is None:
            from core.infrastructure.database.manager import get_db_manager

            self._db = get_db_manager()
        else:
            self._db = db_manager

        self._lock = asyncio.Lock()

    async def add_record(
        self,
        channel: str,
        summary_msg_id: int,
        poll_msg_id: int,
        button_msg_id: int,
        summary_text: str,
        channel_name: str,
        send_to_channel: bool,
        discussion_forward_msg_id: int | None = None,
    ) -> None:
        """添加一条投票重新生成记录

        Args:
            channel: 频道 URL
            summary_msg_id: 总结消息 ID
            poll_msg_id: 投票消息 ID
            button_msg_id: 按钮消息 ID
            summary_text: 总结文本
            channel_name: 频道名称
            send_to_channel: 是否发送到频道
            discussion_forward_msg_id: 讨论组中的转发消息 ID（仅讨论组模式）
        """
        try:
            await self._db.add_poll_regeneration(
                channel=channel,
                summary_msg_id=summary_msg_id,
                poll_msg_id=poll_msg_id,
                button_msg_id=button_msg_id,
                summary_text=summary_text,
                channel_name=channel_name,
                send_to_channel=send_to_channel,
                discussion_forward_msg_id=discussion_forward_msg_id,
            )
        except Exception as e:
            raise DatabaseError(f"添加记录失败: {e}") from e

    async def get_record(self, channel: str, summary_msg_id: int) -> PollRegenerationRecord | None:
        """获取指定的投票重新生成记录

        Args:
            channel: 频道 URL
            summary_msg_id: 总结消息 ID

        Returns:
            投票重新生成记录，如果不存在返回 None
        """
        try:
            return await self._db.get_poll_regeneration(channel, summary_msg_id)
        except Exception as e:
            raise DatabaseError(f"获取记录失败: {e}") from e

    async def update_message_ids(
        self, channel: str, summary_msg_id: int, poll_msg_id: int, button_msg_id: int
    ) -> None:
        """更新投票重新生成记录的消息 ID

        Args:
            channel: 频道 URL
            summary_msg_id: 总结消息 ID
            poll_msg_id: 新的投票消息 ID
            button_msg_id: 新的按钮消息 ID
        """
        try:
            await self._db.update_poll_message_ids(
                channel, summary_msg_id, poll_msg_id, button_msg_id
            )
        except Exception as e:
            raise DatabaseError(f"更新记录失败: {e}") from e

    async def delete_record(self, channel: str, summary_msg_id: int) -> None:
        """删除指定的投票重新生成记录

        Args:
            channel: 频道 URL
            summary_msg_id: 总结消息 ID
        """
        try:
            await self._db.delete_poll_regeneration(channel, summary_msg_id)
        except Exception as e:
            raise DatabaseError(f"删除记录失败: {e}") from e

    async def increment_vote_count(
        self, channel: str, summary_msg_id: int, user_id: int
    ) -> tuple[bool, int, bool]:
        """增加投票计数

        Args:
            channel: 频道 URL
            summary_msg_id: 总结消息 ID
            user_id: 用户 ID

        Returns:
            tuple: (是否成功增加, 当前计数, 是否已投票)
        """
        try:
            return await self._db.increment_vote_count(channel, summary_msg_id, user_id)
        except Exception as e:
            raise DatabaseError(f"增加投票计数失败: {e}") from e

    async def reset_vote_count(self, channel: str, summary_msg_id: int) -> bool:
        """重置投票计数

        Args:
            channel: 频道 URL
            summary_msg_id: 总结消息 ID

        Returns:
            是否成功重置
        """
        try:
            return await self._db.reset_vote_count(channel, summary_msg_id)
        except Exception as e:
            raise DatabaseError(f"重置投票计数失败: {e}") from e

    async def get_vote_count(self, channel: str, summary_msg_id: int) -> int:
        """获取投票计数

        Args:
            channel: 频道 URL
            summary_msg_id: 总结消息 ID

        Returns:
            投票计数，如果记录不存在返回 0
        """
        try:
            return await self._db.get_vote_count(channel, summary_msg_id)
        except Exception as e:
            raise DatabaseError(f"获取投票计数失败: {e}") from e

    async def cleanup_old_records(self, days: int = CLEANUP_DAYS_DEFAULT) -> int:
        """清理超过指定天数的旧记录

        Args:
            days: 保留天数，默认 30 天

        Returns:
            清理的记录数量
        """
        try:
            return await self._db.cleanup_old_poll_regenerations(days)
        except Exception as e:
            raise DatabaseError(f"清理旧记录失败: {e}") from e


# 全局数据管理器实例
_poll_regeneration_manager: PollRegenerationManager | None = None


def get_poll_regeneration_manager() -> PollRegenerationManager:
    """获取全局投票重新生成数据管理器（单例模式）

    Returns:
        PollRegenerationManager 实例
    """
    global _poll_regeneration_manager
    if _poll_regeneration_manager is None:
        _poll_regeneration_manager = PollRegenerationManager()
        logger.info("投票重新生成数据管理器已初始化")
    return _poll_regeneration_manager

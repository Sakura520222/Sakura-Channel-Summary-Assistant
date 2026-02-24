# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可，
# 并附加非商业使用限制条款。

"""
测试 QAUserSystem 模块
重点测试日期格式化功能的跨数据库兼容性
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.qa_user_system import QAUserSystem


class TestFormatDateField:
    """测试 _format_date_field 方法的各种场景"""

    def setup_method(self):
        """每个测试前创建 QAUserSystem 实例"""
        # Mock 数据库管理器
        with patch("core.qa_user_system.get_db_manager"):
            self.qa_system = QAUserSystem()

    def test_format_datetime_object(self):
        """测试格式化 datetime 对象（MySQL 模式）"""
        # 创建一个 datetime 对象
        dt = datetime(2026, 2, 24, 12, 30, 45, tzinfo=UTC)
        result = self.qa_system._format_date_field(dt)
        assert result == "2026-02-24"

    def test_format_datetime_without_timezone(self):
        """测试格式化不带时区的 datetime 对象"""
        dt = datetime(2026, 2, 24, 12, 30, 45)
        result = self.qa_system._format_date_field(dt)
        assert result == "2026-02-24"

    def test_format_string_date(self):
        """测试格式化字符串日期（SQLite 模式）"""
        date_str = "2026-02-24 12:30:45"
        result = self.qa_system._format_date_field(date_str)
        assert result == "2026-02-24"

    def test_format_string_with_iso_format(self):
        """测试格式化 ISO 格式字符串"""
        date_str = "2026-02-24T12:30:45+00:00"
        result = self.qa_system._format_date_field(date_str)
        assert result == "2026-02-24"

    def test_format_none_value(self):
        """测试格式化 None 值"""
        result = self.qa_system._format_date_field(None)
        assert result == ""

    def test_format_empty_string(self):
        """测试格式化空字符串"""
        result = self.qa_system._format_date_field("")
        assert result == ""

    def test_format_short_string(self):
        """测试格式化短字符串（少于10个字符）应返回空字符串"""
        short_str = "2026-02"
        result = self.qa_system._format_date_field(short_str)
        assert result == ""

    def test_format_invalid_string_format(self):
        """测试格式化无效的字符串格式应返回空字符串"""
        invalid_str = "not-a-date"
        result = self.qa_system._format_date_field(invalid_str)
        assert result == ""

    def test_format_string_with_spaces(self):
        """测试格式化带空格的字符串"""
        date_str = "  2026-02-24  "
        result = self.qa_system._format_date_field(date_str)
        assert result == "2026-02-24"

    def test_format_invalid_yyyy_mm_dd(self):
        """测试格式化不符合 YYYY-MM-DD 格式的字符串"""
        invalid_str = "2026/02/24"
        result = self.qa_system._format_date_field(invalid_str)
        assert result == ""

    def test_format_numeric_timestamp(self):
        """测试格式化数字时间戳应返回空字符串"""
        timestamp = 1706109045
        result = self.qa_system._format_date_field(timestamp)
        assert result == ""

    def test_format_random_object(self):
        """测试格式化随机对象应返回空字符串"""
        random_obj = {"key": "value"}
        result = self.qa_system._format_date_field(random_obj)
        assert result == ""

    def test_format_date_object(self):
        """测试格式化 date 对象（不含时间）"""
        from datetime import date

        date_obj = date(2026, 2, 24)
        result = self.qa_system._format_date_field(date_obj)
        assert result == "2026-02-24"


class TestFormatChannelsList:
    """测试 format_channels_list 方法"""

    def setup_method(self):
        """每个测试前创建 QAUserSystem 实例"""
        with patch("core.qa_user_system.get_db_manager"):
            self.qa_system = QAUserSystem()

    def test_format_empty_channels_list(self):
        """测试空频道列表"""
        result = self.qa_system.format_channels_list([])
        assert result == "暂无可订阅的频道。"

    def test_format_channels_with_datetime(self):
        """测试格式化包含 datetime 对象的频道列表（MySQL 模式）"""
        channels = [
            {
                "channel_id": "https://t.me/test_channel1",
                "channel_name": "测试频道1",
                "last_summary_time": datetime(2026, 2, 24, 12, 30, 45, tzinfo=UTC),
            },
            {
                "channel_id": "https://t.me/test_channel2",
                "channel_name": "测试频道2",
                "last_summary_time": datetime(2026, 2, 23, 10, 15, 30),
            },
        ]
        result = self.qa_system.format_channels_list(channels)

        assert "📋 **可订阅频道列表**" in result
        assert "**测试频道1**" in result
        assert "**测试频道2**" in result
        assert "最后更新: 2026-02-24" in result
        assert "最后更新: 2026-02-23" in result
        assert "https://t.me/test_channel1" in result
        assert "https://t.me/test_channel2" in result
        assert "/subscribe" in result

    def test_format_channels_with_string_dates(self):
        """测试格式化包含字符串日期的频道列表（SQLite 模式）"""
        channels = [
            {
                "channel_id": "https://t.me/test_channel1",
                "channel_name": "测试频道1",
                "last_summary_time": "2026-02-24 12:30:45",
            },
            {
                "channel_id": "https://t.me/test_channel2",
                "channel_name": "测试频道2",
                "last_summary_time": "2026-02-23T10:15:30",
            },
        ]
        result = self.qa_system.format_channels_list(channels)

        assert "📋 **可订阅频道列表**" in result
        assert "最后更新: 2026-02-24" in result
        assert "最后更新: 2026-02-23" in result

    def test_format_channels_with_none_dates(self):
        """测试格式化包含 None 日期的频道列表"""
        channels = [
            {
                "channel_id": "https://t.me/test_channel1",
                "channel_name": "测试频道1",
                "last_summary_time": None,
            },
        ]
        result = self.qa_system.format_channels_list(channels)

        assert "📋 **可订阅频道列表**" in result
        assert "最后更新: " in result  # 应该显示空字符串

    def test_format_channels_with_missing_fields(self):
        """测试格式化缺少字段的频道列表"""
        channels = [
            {
                "channel_id": "https://t.me/test_channel1",
                # 缺少 channel_name 和 last_summary_time
            },
        ]
        result = self.qa_system.format_channels_list(channels)

        assert "📋 **可订阅频道列表**" in result
        assert "**未知频道**" in result
        assert "最后更新: " in result

    def test_format_channels_single_channel(self):
        """测试格式化单个频道"""
        channels = [
            {
                "channel_id": "https://t.me/single_channel",
                "channel_name": "单独频道",
                "last_summary_time": "2026-02-24 12:30:45",
            }
        ]
        result = self.qa_system.format_channels_list(channels)

        assert "1. **单独频道**" in result
        assert "/subscribe https://t.me/single_channel" in result


class TestFormatSubscriptionsList:
    """测试 format_subscriptions_list 方法"""

    def setup_method(self):
        """每个测试前创建 QAUserSystem 实例"""
        with patch("core.qa_user_system.get_db_manager"):
            self.qa_system = QAUserSystem()

    def test_format_empty_subscriptions_list(self):
        """测试空订阅列表"""
        result = self.qa_system.format_subscriptions_list([])
        assert "您还没有订阅任何频道" in result
        assert "/listchannels" in result

    def test_format_subscriptions_with_datetime(self):
        """测试格式化包含 datetime 对象的订阅列表（MySQL 模式）"""
        subscriptions = [
            {
                "channel_id": "https://t.me/test_channel1",
                "channel_name": "测试频道1",
                "created_at": datetime(2026, 2, 20, 12, 30, 45, tzinfo=UTC),
            },
            {
                "channel_id": "https://t.me/test_channel2",
                "channel_name": "测试频道2",
                "created_at": datetime(2026, 2, 21, 10, 15, 30),
            },
        ]
        result = self.qa_system.format_subscriptions_list(subscriptions)

        assert "📚 **我的订阅**" in result
        assert "**测试频道1**" in result
        assert "**测试频道2**" in result
        assert "订阅时间: 2026-02-20" in result
        assert "订阅时间: 2026-02-21" in result
        assert "/unsubscribe" in result

    def test_format_subscriptions_with_string_dates(self):
        """测试格式化包含字符串日期的订阅列表（SQLite 模式）"""
        subscriptions = [
            {
                "channel_id": "https://t.me/test_channel1",
                "channel_name": "测试频道1",
                "created_at": "2026-02-20 12:30:45",
            },
            {
                "channel_id": "https://t.me/test_channel2",
                "channel_name": "测试频道2",
                "created_at": "2026-02-21T10:15:30",
            },
        ]
        result = self.qa_system.format_subscriptions_list(subscriptions)

        assert "📚 **我的订阅**" in result
        assert "订阅时间: 2026-02-20" in result
        assert "订阅时间: 2026-02-21" in result

    def test_format_subscriptions_with_none_dates(self):
        """测试格式化包含 None 日期的订阅列表"""
        subscriptions = [
            {
                "channel_id": "https://t.me/test_channel1",
                "channel_name": "测试频道1",
                "created_at": None,
            },
        ]
        result = self.qa_system.format_subscriptions_list(subscriptions)

        assert "📚 **我的订阅**" in result
        assert "订阅时间: " in result  # 应该显示空字符串

    def test_format_subscriptions_with_missing_channel_name(self):
        """测试格式化缺少频道名称的订阅列表"""
        subscriptions = [
            {
                "channel_id": "https://t.me/test_channel1",
                # 缺少 channel_name
                "created_at": "2026-02-20 12:30:45",
            },
        ]
        result = self.qa_system.format_subscriptions_list(subscriptions)

        assert "📚 **我的订阅**" in result
        assert "https://t.me/test_channel1" in result  # 应该使用 channel_id 作为名称

    def test_format_subscriptions_single_subscription(self):
        """测试格式化单个订阅"""
        subscriptions = [
            {
                "channel_id": "https://t.me/single_channel",
                "channel_name": "单独订阅",
                "created_at": "2026-02-20 12:30:45",
            }
        ]
        result = self.qa_system.format_subscriptions_list(subscriptions)

        assert "1. **单独订阅**" in result
        assert "/unsubscribe https://t.me/single_channel" in result


class TestQAUserSystemAsyncMethods:
    """测试 QAUserSystem 的异步方法"""

    @pytest.fixture
    def qa_system_with_mock_db(self):
        """创建带有 mock 数据库的 QAUserSystem 实例"""
        mock_db = MagicMock()
        mock_db.is_user_registered = AsyncMock(return_value=False)
        mock_db.register_user = AsyncMock(return_value=True)
        mock_db.update_user_activity = AsyncMock(return_value=True)
        mock_db.get_all_channels = AsyncMock(return_value=[])
        mock_db.is_subscribed = AsyncMock(return_value=False)
        mock_db.add_subscription = AsyncMock(return_value=True)
        mock_db.remove_subscription = AsyncMock(return_value=1)
        mock_db.get_user_subscriptions = AsyncMock(return_value=[])
        mock_db.create_request = MagicMock(return_value=123)
        mock_db.get_request_status = MagicMock(return_value=None)

        with patch("core.qa_user_system.get_db_manager", return_value=mock_db):
            qa_system = QAUserSystem()
            qa_system.db = mock_db
            return qa_system

    @pytest.mark.asyncio
    async def test_register_new_user(self, qa_system_with_mock_db):
        """测试注册新用户"""
        result = await qa_system_with_mock_db.register_user(
            user_id=123456, username="testuser", first_name="Test"
        )

        assert result["success"] is True
        assert result["new_user"] is True
        assert "注册成功" in result["message"]

    @pytest.mark.asyncio
    async def test_register_existing_user(self, qa_system_with_mock_db):
        """测试已存在的用户"""
        qa_system_with_mock_db.db.is_user_registered = AsyncMock(return_value=True)

        result = await qa_system_with_mock_db.register_user(user_id=123456)

        assert result["success"] is True
        assert result["new_user"] is False
        assert "欢迎回来" in result["message"]

    @pytest.mark.asyncio
    async def test_get_available_channels(self, qa_system_with_mock_db):
        """测试获取可用频道列表"""
        test_channels = [
            {
                "channel_id": "https://t.me/test1",
                "channel_name": "测试频道1",
                "last_summary_time": datetime(2026, 2, 24, 12, 30, 45),
            }
        ]
        qa_system_with_mock_db.db.get_all_channels = AsyncMock(return_value=test_channels)

        channels = await qa_system_with_mock_db.get_available_channels()

        assert len(channels) == 1
        assert channels[0]["channel_name"] == "测试频道1"

    @pytest.mark.asyncio
    async def test_add_subscription_success(self, qa_system_with_mock_db):
        """测试成功添加订阅"""
        result = await qa_system_with_mock_db.add_subscription(
            user_id=123456, channel_id="https://t.me/test", channel_name="测试频道"
        )

        assert result["success"] is True
        assert "已订阅" in result["message"]

    @pytest.mark.asyncio
    async def test_add_subscription_already_exists(self, qa_system_with_mock_db):
        """测试添加已存在的订阅"""
        qa_system_with_mock_db.db.is_subscribed = AsyncMock(return_value=True)

        result = await qa_system_with_mock_db.add_subscription(
            user_id=123456, channel_id="https://t.me/test", channel_name="测试频道"
        )

        assert result["success"] is False
        assert "已经订阅" in result["message"]

    @pytest.mark.asyncio
    async def test_remove_subscription_success(self, qa_system_with_mock_db):
        """测试成功移除订阅"""
        result = await qa_system_with_mock_db.remove_subscription(
            user_id=123456, channel_id="https://t.me/test"
        )

        assert result["success"] is True
        assert "已取消" in result["message"]

    @pytest.mark.asyncio
    async def test_get_user_subscriptions(self, qa_system_with_mock_db):
        """测试获取用户订阅列表"""
        test_subs = [
            {
                "channel_id": "https://t.me/test1",
                "channel_name": "测试频道1",
                "created_at": "2026-02-20 12:30:45",
            }
        ]
        qa_system_with_mock_db.db.get_user_subscriptions = AsyncMock(return_value=test_subs)

        subscriptions = await qa_system_with_mock_db.get_user_subscriptions(123456)

        assert len(subscriptions) == 1
        assert subscriptions[0]["channel_name"] == "测试频道1"

    def test_create_summary_request(self, qa_system_with_mock_db):
        """测试创建总结请求（同步方法）"""
        result = qa_system_with_mock_db.create_summary_request(
            user_id=123456, channel_id="https://t.me/test", channel_name="测试频道"
        )

        assert result["success"] is True
        assert result["request_id"] == 123
        assert "已向管理员提交" in result["message"]

    def test_get_request_status(self, qa_system_with_mock_db):
        """测试获取请求状态（同步方法）"""
        qa_system_with_mock_db.db.get_request_status = MagicMock(return_value=None)

        result = qa_system_with_mock_db.get_request_status(123)

        assert result is None

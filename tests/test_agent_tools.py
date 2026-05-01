# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""测试 Agentic RAG 工具执行器"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.ai.agent_tools import TOOL_SCHEMAS, ToolExecutor


@pytest.fixture
def executor():
    """创建工具执行器"""
    vector_store = MagicMock()
    vector_store.is_available.return_value = True
    vector_store.is_messages_available.return_value = True
    memory_manager = MagicMock()
    reranker = MagicMock()
    reranker.is_available.return_value = False
    return ToolExecutor(vector_store, memory_manager, reranker)


def test_tool_schemas_include_channel_tools():
    """测试工具定义包含频道相关工具"""
    names = {tool["function"]["name"] for tool in TOOL_SCHEMAS}

    assert "list_channels" in names
    assert "resolve_channel" in names
    assert "get_recent_summaries" in names
    assert "get_channel_stats" in names
    assert "get_source_detail" in names


@pytest.mark.asyncio
async def test_execute_list_channels_returns_channels(executor):
    """测试列出频道工具"""
    executor.memory_manager.list_channels = AsyncMock(
        return_value=[
            {"channel_id": "https://t.me/test", "channel_name": "Test", "summary_count": 1}
        ]
    )

    result = json.loads(await executor.execute("list_channels", {"limit": 10}))

    assert result["count"] == 1
    assert result["channels"][0]["channel_id"] == "https://t.me/test"


@pytest.mark.asyncio
async def test_execute_resolve_channel_returns_match(executor):
    """测试解析频道工具"""
    executor.memory_manager.resolve_channel = AsyncMock(
        return_value={"success": True, "channel_id": "https://t.me/test"}
    )

    result = json.loads(await executor.execute("resolve_channel", {"channel_hint": "@test"}))

    assert result["success"] is True
    assert result["channel_id"] == "https://t.me/test"


@pytest.mark.asyncio
async def test_execute_semantic_search_uses_channel_filter(executor):
    """测试语义检索传递频道过滤"""
    executor.vector_store.search_all.return_value = [
        {
            "summary_id": 1,
            "summary_text": "完整内容",
            "metadata": {"channel_id": "https://t.me/test", "channel_name": "Test"},
            "doc_id": "https://t.me/test:1",
            "source": "message",
        }
    ]

    result = json.loads(
        await executor.execute(
            "semantic_search",
            {"query": "AI", "channel_id": "https://t.me/test", "collection": "all"},
        )
    )

    assert result["count"] == 1
    executor.vector_store.search_all.assert_called_once()
    call_kwargs = executor.vector_store.search_all.call_args.kwargs
    assert call_kwargs["filter_metadata"] == {"channel_id": "https://t.me/test"}


@pytest.mark.asyncio
async def test_execute_source_detail_returns_full_text(executor):
    """测试来源详情返回完整文本"""
    executor.vector_store.search_all.return_value = [
        {
            "summary_id": 1,
            "summary_text": "很长的完整内容" * 100,
            "metadata": {"channel_id": "https://t.me/test", "channel_name": "Test"},
            "doc_id": "https://t.me/test:1",
        }
    ]
    await executor.execute("semantic_search", {"query": "AI"})

    result = json.loads(await executor.execute("get_source_detail", {"summary_id": 1}))

    assert "detail" in result
    assert len(result["detail"]["summary_text"]) > 500

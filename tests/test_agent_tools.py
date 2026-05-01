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


def test_serialize_result_builds_message_post_link():
    """测试消息向量结果会生成帖子链接"""
    result = {
        "summary_id": 1,
        "summary_text": "消息内容",
        "doc_id": "https://t.me/test:123",
        "metadata": {"channel_id": "https://t.me/test", "channel_name": "Test"},
    }

    serialized = ToolExecutor._serialize_result(result)

    assert serialized["post_links"] == ["https://t.me/test/123"]


def test_build_summary_post_links_uses_summary_message_ids():
    """测试总结结果会根据 summary_message_ids 生成帖子链接"""
    summary = {
        "channel_id": "https://t.me/test",
        "summary_message_ids": [10, 11, 12],
    }

    links = ToolExecutor._build_summary_post_links(summary)

    assert links == [
        "https://t.me/test/10",
        "https://t.me/test/11",
        "https://t.me/test/12",
    ]


def test_serialize_result_builds_summary_post_links_from_metadata_json():
    """测试总结向量元数据中的消息 ID 会生成帖子链接"""
    result = {
        "summary_id": 1,
        "summary_text": "总结内容",
        "metadata": {
            "channel_id": "https://t.me/test",
            "channel_name": "Test",
            "summary_message_ids": "[10, 11]",
        },
        "source": "summary",
    }

    serialized = ToolExecutor._serialize_result(result)

    assert serialized["post_links"] == ["https://t.me/test/10", "https://t.me/test/11"]


def test_build_post_link_rejects_invalid_sources():
    """测试帖子链接构造会拒绝无效或私有来源"""
    assert ToolExecutor._build_post_link(None, 1) is None
    assert ToolExecutor._build_post_link("https://t.me/+private", 1) is None
    assert ToolExecutor._build_post_link("https://t.me/test", "abc") is None
    assert ToolExecutor._build_post_link("@test_channel", 123) == "https://t.me/test_channel/123"


def test_get_all_results_includes_doc_results_without_duplicates(executor):
    """测试获取全部结果时包含仅 doc_id 索引的消息结果并去重"""
    summary_result = {"summary_id": 1, "summary_text": "总结"}
    message_result = {"summary_text": "消息", "doc_id": "https://t.me/test:2"}
    duplicated_result = {
        "summary_id": 3,
        "summary_text": "同时有两个索引",
        "doc_id": "https://t.me/test:3",
    }

    executor._store_result(summary_result)
    executor._store_result(message_result)
    executor._store_result(duplicated_result)

    results = executor.get_all_results()

    assert summary_result in results
    assert message_result in results
    assert results.count(duplicated_result) == 1


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
    assert result["results"][0]["post_links"] == ["https://t.me/test/1"]
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

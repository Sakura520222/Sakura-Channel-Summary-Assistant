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
Agentic RAG 工具定义与执行器
将检索能力封装为 LLM 可调用的 Function Calling 工具
"""

import asyncio
import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OpenAI 兼容的工具 Schema 定义
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "semantic_search",
            "description": (
                "搜索与查询语义相关的频道历史总结和消息。"
                "使用向量相似度检索，适合模糊匹配和概念性查询。"
                "当用户询问某个主题、概念或需要广泛召回时使用此工具。"
                "默认同时搜索总结和原始消息两个数据源。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询文本，应使用改写后的完整独立查询。",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量，默认20",
                        "default": 20,
                    },
                    "date_after": {
                        "type": "string",
                        "description": "时间下限，ISO格式，如 '2026-04-19T00:00:00'",
                    },
                    "date_before": {
                        "type": "string",
                        "description": "时间上限，ISO格式",
                    },
                    "channel_id": {
                        "type": "string",
                        "description": "限定搜索的频道ID",
                    },
                    "collection": {
                        "type": "string",
                        "description": "搜索的数据源: 'all'(默认，同时搜summaries+messages)、'summaries'(仅总结)、'messages'(仅原始消息)",
                        "enum": ["all", "summaries", "messages"],
                        "default": "all",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "keyword_search",
            "description": (
                "基于关键词搜索频道历史总结。"
                "使用SQL匹配，适合精确关键词查找和补充语义检索的结果。"
                "当语义搜索结果不足、需要查找特定术语，或需要按频道/时间获取最近总结时使用。"
                "keywords 可为空；为空时将按 channel_id/time_range_days/limit 做频道或时间过滤。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "关键词列表",
                    },
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "主题列表，如 ['技术', 'AI']",
                    },
                    "time_range_days": {
                        "type": "integer",
                        "description": "搜索最近N天的总结，默认90",
                        "default": 90,
                    },
                    "channel_id": {
                        "type": "string",
                        "description": "限定搜索的频道ID",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量上限，默认10",
                        "default": 10,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_channels",
            "description": "获取所有可查询频道的名称、链接、总结数和最后更新时间。用户询问频道链接、有哪些频道、可查询范围时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回频道数量上限，默认50",
                        "default": 50,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "resolve_channel",
            "description": "根据频道名、@username、t.me链接或模糊名称解析为标准频道链接。限定频道查询前应先调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_hint": {
                        "type": "string",
                        "description": "用户提到的频道名称、@username 或 Telegram 链接",
                    },
                },
                "required": ["channel_hint"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_summaries",
            "description": "获取指定频道或所有频道的最近总结，适合回答最近发生了什么、最新动态等问题。",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "可选，限定频道链接。若用户给的是频道名，应先调用 resolve_channel。",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回总结数量，默认5",
                        "default": 5,
                    },
                    "time_range_days": {
                        "type": "integer",
                        "description": "可选，最近N天",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_channel_stats",
            "description": "获取指定频道的总结数量、消息数量和更新时间等统计信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "标准频道链接。若用户给的是频道名，应先调用 resolve_channel。",
                    },
                },
                "required": ["channel_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_source_detail",
            "description": "按 summary_id 或 doc_id 获取之前搜索结果中的完整来源内容。用户要求展开来源、查看详情时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary_id": {
                        "type": "integer",
                        "description": "搜索结果中的 summary_id",
                    },
                    "doc_id": {
                        "type": "string",
                        "description": "搜索结果中的原始 doc_id，适用于消息向量来源",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rerank_results",
            "description": (
                "对搜索结果进行精排重排序。"
                "当搜索结果较多(>5条)且需要提高准确率时使用。"
                "基于query与文档的相关性重新排序并返回Top-K结果。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用于重排序的查询文本",
                    },
                    "result_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "需要重排序的结果ID列表（从之前搜索结果中选取）",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "重排序后保留的结果数量，默认5",
                        "default": 5,
                    },
                },
                "required": ["query", "result_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_channel_info",
            "description": (
                "获取频道列表和频道画像信息。当用户提及特定频道或需要了解可用频道时使用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "频道ID，不传则返回所有频道列表",
                    },
                },
                "required": [],
            },
        },
    },
]

# 在 tool message 中截断 summary_text 的最大字符数
_SUMMARY_TRUNCATE_LEN = 500


class ToolExecutor:
    """工具执行器：将 LLM 的 tool_call 请求路由到实际的检索组件。"""

    def __init__(self, vector_store, memory_manager, reranker):
        self.vector_store = vector_store
        self.memory_manager = memory_manager
        self.reranker = reranker
        # 累积所有搜索结果，供 rerank_results 按 ID 引用
        self._result_store: dict[int, dict[str, Any]] = {}
        self._doc_result_store: dict[str, dict[str, Any]] = {}

    def reset(self):
        """重置结果存储（每次 agent loop 开始时调用）"""
        self._result_store.clear()
        self._doc_result_store.clear()

    async def execute(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """执行工具调用，返回 JSON 字符串格式的结果。

        所有异常都被捕获并作为错误结果返回，不会向上抛出。
        """
        try:
            if tool_name == "semantic_search":
                return await self._execute_semantic_search(arguments)
            elif tool_name == "keyword_search":
                return await self._execute_keyword_search(arguments)
            elif tool_name == "rerank_results":
                return await self._execute_rerank(arguments)
            elif tool_name == "list_channels":
                return await self._execute_list_channels(arguments)
            elif tool_name == "resolve_channel":
                return await self._execute_resolve_channel(arguments)
            elif tool_name == "get_recent_summaries":
                return await self._execute_recent_summaries(arguments)
            elif tool_name == "get_channel_stats":
                return await self._execute_channel_stats(arguments)
            elif tool_name == "get_source_detail":
                return await self._execute_source_detail(arguments)
            elif tool_name == "get_channel_info":
                return await self._execute_channel_info(arguments)
            else:
                return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
        except Exception as e:
            logger.error(f"工具执行失败 [{tool_name}]: {type(e).__name__}: {e}", exc_info=True)
            return json.dumps(
                {"error": f"工具执行失败: {type(e).__name__}: {e}"}, ensure_ascii=False
            )

    # ---- 各工具实现 ----

    async def _execute_semantic_search(self, args: dict) -> str:
        if not self.vector_store.is_available():
            return json.dumps(
                {"error": "向量存储不可用", "results": [], "count": 0}, ensure_ascii=False
            )

        filter_metadata = None
        if args.get("channel_id"):
            filter_metadata = {"channel_id": args["channel_id"]}

        # 根据 collection 参数选择数据源
        collection = args.get("collection", "all")

        if collection == "messages" and self.vector_store.is_messages_available():
            results = self.vector_store.search_messages(
                query=args["query"],
                top_k=args.get("top_k", 20),
                filter_metadata=filter_metadata,
                date_after=args.get("date_after"),
                date_before=args.get("date_before"),
            )
        elif collection == "summaries":
            results = self.vector_store.search_similar(
                query=args["query"],
                top_k=args.get("top_k", 20),
                filter_metadata=filter_metadata,
                date_after=args.get("date_after"),
                date_before=args.get("date_before"),
            )
        else:
            # 默认: 同时搜索 summaries + messages
            if self.vector_store.is_messages_available():
                results = self.vector_store.search_all(
                    query=args["query"],
                    top_k=args.get("top_k", 20),
                    filter_metadata=filter_metadata,
                    date_after=args.get("date_after"),
                    date_before=args.get("date_before"),
                )
            else:
                results = self.vector_store.search_similar(
                    query=args["query"],
                    top_k=args.get("top_k", 20),
                    filter_metadata=filter_metadata,
                    date_after=args.get("date_after"),
                    date_before=args.get("date_before"),
                )

        # 累积到 result_store 并序列化（截断长文本）
        serialized = []
        for r in results:
            self._store_result(r)
            serialized.append(self._serialize_result(r))

        return json.dumps(
            {"results": serialized, "count": len(serialized)},
            ensure_ascii=False,
        )

    async def _execute_keyword_search(self, args: dict) -> str:
        results = await self.memory_manager.search_summaries(
            keywords=args.get("keywords", []),
            topics=args.get("topics"),
            time_range_days=args.get("time_range_days", 90),
            channel_id=args.get("channel_id"),
            limit=args.get("limit", 10),
        )

        # keyword_search 返回原始 DB 行，需要归一化为统一格式
        serialized = []
        for r in results:
            sid = r.get("id")
            if sid is None:
                continue
            post_links = self._build_summary_post_links(r)
            normalized = {
                "summary_id": sid,
                "summary_text": r.get("summary_text", ""),
                "post_links": post_links,
                "metadata": {
                    "channel_id": r.get("channel_id"),
                    "channel_name": r.get("channel_name"),
                    "created_at": r.get("created_at"),
                    "post_links": post_links,
                },
            }
            self._store_result(normalized)
            serialized.append(self._serialize_result(normalized))

        return json.dumps(
            {"results": serialized, "count": len(serialized)},
            ensure_ascii=False,
        )

    async def _execute_rerank(self, args: dict) -> str:
        if not self.reranker.is_available():
            return json.dumps(
                {"error": "重排序服务不可用", "results": [], "count": 0}, ensure_ascii=False
            )

        result_ids = args.get("result_ids", [])
        candidates = [self._result_store[rid] for rid in result_ids if rid in self._result_store]

        if not candidates:
            return json.dumps(
                {"error": "未找到有效的结果ID", "results": [], "count": 0}, ensure_ascii=False
            )

        loop = asyncio.get_running_loop()
        reranked = await loop.run_in_executor(
            None,
            lambda: self.reranker.rerank(
                query=args["query"],
                candidates=candidates,
                top_k=args.get("top_k", 5),
            ),
        )

        # 更新 result_store 中的结果（含 rerank_score）
        serialized = []
        for r in reranked:
            self._store_result(r)
            serialized.append(self._serialize_result(r))

        return json.dumps(
            {"results": serialized, "count": len(serialized)},
            ensure_ascii=False,
        )

    async def _execute_list_channels(self, args: dict) -> str:
        channels = await self.memory_manager.list_channels()
        limit = max(1, min(int(args.get("limit", 50)), 100))
        return json.dumps(
            {
                "channels": channels[:limit],
                "count": min(len(channels), limit),
                "total": len(channels),
            },
            ensure_ascii=False,
        )

    async def _execute_resolve_channel(self, args: dict) -> str:
        result = await self.memory_manager.resolve_channel(args.get("channel_hint", ""))
        return json.dumps(result, ensure_ascii=False)

    async def _execute_recent_summaries(self, args: dict) -> str:
        results = await self.memory_manager.get_recent_summaries(
            channel_id=args.get("channel_id"),
            limit=args.get("limit", 5),
            time_range_days=args.get("time_range_days"),
        )
        serialized = []
        for r in results:
            sid = r.get("id") or r.get("summary_id")
            if sid is None:
                continue
            post_links = self._build_summary_post_links(r)
            normalized = {
                "summary_id": sid,
                "summary_text": r.get("summary_text", ""),
                "post_links": post_links,
                "metadata": {
                    "channel_id": r.get("channel_id"),
                    "channel_name": r.get("channel_name"),
                    "created_at": r.get("created_at"),
                    "post_links": post_links,
                },
                "source": "summary",
            }
            self._store_result(normalized)
            serialized.append(self._serialize_result(normalized))

        return json.dumps({"results": serialized, "count": len(serialized)}, ensure_ascii=False)

    async def _execute_channel_stats(self, args: dict) -> str:
        stats = await self.memory_manager.get_channel_stats(args.get("channel_id", ""))
        return json.dumps({"stats": stats}, ensure_ascii=False)

    async def _execute_source_detail(self, args: dict) -> str:
        result = None
        summary_id = args.get("summary_id")
        doc_id = args.get("doc_id")

        if summary_id is not None:
            result = self._result_store.get(summary_id)

        if result is None and doc_id:
            result = self._doc_result_store.get(str(doc_id))

        if result is None:
            return json.dumps(
                {"error": "未找到来源详情，请先执行搜索或提供有效的 summary_id/doc_id"},
                ensure_ascii=False,
            )

        detail = self._serialize_result(result)
        detail["summary_text"] = result.get("summary_text", "")
        return json.dumps({"detail": detail}, ensure_ascii=False)

    async def _execute_channel_info(self, args: dict) -> str:
        channel_id = args.get("channel_id")
        if not channel_id:
            channels = await self.memory_manager.list_channels()
            return json.dumps({"channels": channels, "count": len(channels)}, ensure_ascii=False)

        context = await self.memory_manager.get_channel_context(channel_id)

        if channel_id:
            return json.dumps({"channel_id": channel_id, "context": context}, ensure_ascii=False)

        # 无 channel_id 时返回通用信息
        return json.dumps({"context": context}, ensure_ascii=False)

    # ---- 辅助方法 ----

    @staticmethod
    def _serialize_result(result: dict) -> dict:
        """序列化单条结果用于 tool message（截断长文本）。"""
        text = result.get("summary_text", "")
        truncated = (
            text[:_SUMMARY_TRUNCATE_LEN] + "..." if len(text) > _SUMMARY_TRUNCATE_LEN else text
        )

        metadata = result.get("metadata", {})
        created_at = metadata.get("created_at")
        if hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()

        serialized = {
            "summary_id": result.get("summary_id"),
            "summary_text": truncated,
            "channel_id": metadata.get("channel_id"),
            "channel_name": metadata.get("channel_name"),
            "created_at": created_at,
            "doc_id": result.get("doc_id"),
            "source": result.get("source"),
            "post_links": ToolExecutor._get_post_links(result),
        }
        if "similarity" in result:
            serialized["similarity"] = round(result["similarity"], 3)
        if "rerank_score" in result:
            serialized["rerank_score"] = round(result["rerank_score"], 3)
        return serialized

    def _store_result(self, result: dict[str, Any]) -> None:
        """缓存搜索结果，供重排序和来源详情工具复用。"""
        sid = result.get("summary_id")
        if sid is not None:
            self._result_store[sid] = result
        doc_id = result.get("doc_id")
        if doc_id:
            self._doc_result_store[str(doc_id)] = result

    @staticmethod
    def _build_summary_post_links(summary: dict[str, Any], max_links: int = 5) -> list[str]:
        """根据总结中的消息 ID 构造 Telegram 帖子链接。"""
        channel_id = summary.get("channel_id") or summary.get("metadata", {}).get("channel_id")
        metadata = summary.get("metadata", {})
        message_ids = (
            summary.get("summary_message_ids") or metadata.get("summary_message_ids") or []
        )
        if isinstance(message_ids, str):
            try:
                message_ids = json.loads(message_ids)
            except json.JSONDecodeError:
                message_ids = []

        return [
            link
            for message_id in message_ids[:max_links]
            if (link := ToolExecutor._build_post_link(channel_id, message_id))
        ]

    @staticmethod
    def _get_post_links(result: dict[str, Any]) -> list[str]:
        """从结果中提取或构造帖子链接。"""
        metadata = result.get("metadata", {})
        links = result.get("post_links") or metadata.get("post_links") or []
        if isinstance(links, str):
            try:
                links = json.loads(links)
            except json.JSONDecodeError:
                links = [links]
        if links:
            return links

        summary_links = ToolExecutor._build_summary_post_links(result)
        if summary_links:
            return summary_links

        doc_id = result.get("doc_id")
        channel_id = metadata.get("channel_id") or result.get("channel_id")
        message_id = metadata.get("message_id") or result.get("message_id")

        if not message_id and doc_id:
            match = re.search(r":(\d+)$", str(doc_id))
            if match:
                message_id = match.group(1)

        link = ToolExecutor._build_post_link(channel_id, message_id)
        return [link] if link else []

    @staticmethod
    def _build_post_link(channel_id: str | None, message_id: Any) -> str | None:
        """构造 Telegram 公开频道帖子链接。"""
        if not channel_id or not message_id:
            return None

        channel = str(channel_id).strip().rstrip("/")
        if "/+" in channel or channel.split("/")[-1].startswith("+"):
            return None

        channel_part = channel.split("/")[-1].lstrip("@")
        if not channel_part or not str(message_id).isdigit():
            return None

        return f"https://t.me/{channel_part}/{message_id}"

    def get_all_results(self) -> list[dict[str, Any]]:
        """获取所有累积的搜索结果（完整文本，不截断）。"""
        all_results = []
        seen_keys = set()
        for result in [*self._result_store.values(), *self._doc_result_store.values()]:
            key = (result.get("summary_id"), result.get("doc_id"))
            if key not in seen_keys:
                all_results.append(result)
                seen_keys.add(key)
        return all_results

    def get_results_by_ids(self, ids: list[int]) -> list[dict[str, Any]]:
        """根据 ID 列表获取结果，按 ID 出现顺序排列。"""
        return [self._result_store[i] for i in ids if i in self._result_store]

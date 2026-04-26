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
                "搜索与查询语义相关的频道历史总结。"
                "使用向量相似度检索，适合模糊匹配和概念性查询。"
                "当用户询问某个主题、概念或需要广泛召回时使用此工具。"
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
                "当语义搜索结果不足或需要查找特定术语时使用。"
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
                "required": ["keywords"],
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

    def reset(self):
        """重置结果存储（每次 agent loop 开始时调用）"""
        self._result_store.clear()

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
            sid = r["summary_id"]
            self._result_store[sid] = r
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
            normalized = {
                "summary_id": sid,
                "summary_text": r.get("summary_text", ""),
                "metadata": {
                    "channel_id": r.get("channel_id"),
                    "channel_name": r.get("channel_name"),
                    "created_at": r.get("created_at"),
                },
            }
            self._result_store[sid] = normalized
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
            sid = r.get("summary_id")
            if sid is not None:
                self._result_store[sid] = r
            serialized.append(self._serialize_result(r))

        return json.dumps(
            {"results": serialized, "count": len(serialized)},
            ensure_ascii=False,
        )

    async def _execute_channel_info(self, args: dict) -> str:
        channel_id = args.get("channel_id")
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
            "channel_name": metadata.get("channel_name"),
            "created_at": created_at,
        }
        if "similarity" in result:
            serialized["similarity"] = round(result["similarity"], 3)
        if "rerank_score" in result:
            serialized["rerank_score"] = round(result["rerank_score"], 3)
        return serialized

    def get_all_results(self) -> list[dict[str, Any]]:
        """获取所有累积的搜索结果（完整文本，不截断）。"""
        return list(self._result_store.values())

    def get_results_by_ids(self, ids: list[int]) -> list[dict[str, Any]]:
        """根据 ID 列表获取结果，按 ID 出现顺序排列。"""
        return [self._result_store[i] for i in ids if i in self._result_store]

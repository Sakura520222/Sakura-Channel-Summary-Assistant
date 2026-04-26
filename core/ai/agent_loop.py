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
Agentic RAG 循环 - LLM 自主决定检索策略的核心循环
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from core.ai.agent_tools import TOOL_SCHEMAS, ToolExecutor
from core.ai.ai_client import client_llm
from core.settings import get_llm_model

logger = logging.getLogger(__name__)

# 最大工具调用迭代次数
MAX_ITERATIONS = 10

# Agent 系统提示词
AGENT_SYSTEM_PROMPT = """\
你是一个智能检索助手，负责根据用户问题调用合适的搜索工具收集相关资料。

## 意图分析（由系统预处理）
{intent_context}

## 当前对话历史
{conversation_context}

## 可用工具
你可以使用以下工具搜索信息：
- **semantic_search**: 语义搜索，适合模糊/概念性查询
- **keyword_search**: 关键词搜索，适合精确匹配特定术语
- **rerank_results**: 对搜索结果重排序（结果>5条时考虑使用）
- **get_channel_info**: 获取频道信息

## 工作策略
1. 分析用户问题，确定需要的搜索方式和参数
2. 可以同时调用多个搜索工具（如语义+关键词并行检索）
3. 评估搜索结果：
   - 如果结果充足，直接基于结果生成回答
   - 如果结果不足，调整参数再次搜索（如扩大时间范围、换关键词）
   - 如果结果过多(>5条)且需要精确，调用 rerank_results
4. 最多进行{max_iterations}轮工具调用

## 输出要求
- 当你收集到足够信息后，直接生成最终回答（不再调用工具）
- 回答必须基于搜索结果，不要编造信息
- 如果搜索无结果，如实告知用户并建议调整查询
- 使用 Markdown 格式，但禁止使用 # 标题格式
"""


@dataclass
class AgentResult:
    """Agent Loop 运行结果"""

    # 最终用于生成回答的摘要列表
    summaries: list[dict[str, Any]] = field(default_factory=list)
    # 使用的迭代次数
    iterations_used: int = 0
    # Agent 最终的文本消息（如果有）
    final_message: str | None = None
    # 是否成功获取结果
    has_results: bool = False


class AgentLoop:
    """Agentic 检索循环"""

    def __init__(self, tool_executor: ToolExecutor):
        self.tool_executor = tool_executor

    async def run(
        self,
        query: str,
        search_query: str,
        intent_parsed: dict[str, Any],
        conversation_history: list[dict],
    ) -> AgentResult:
        """执行 agentic 检索循环。

        Args:
            query: 用户原始查询
            search_query: 改写后的检索查询
            intent_parsed: IntentParser 解析结果
            conversation_history: 对话历史

        Returns:
            AgentResult 包含检索到的摘要和运行统计
        """
        self.tool_executor.reset()

        messages = self._build_initial_messages(
            query, search_query, intent_parsed, conversation_history
        )

        for iteration in range(MAX_ITERATIONS):
            logger.info(f"[agent] 迭代 {iteration + 1}/{MAX_ITERATIONS}")

            # 调用 LLM（带工具定义）
            response = await self._call_llm(messages)

            if response is None:
                logger.warning("[agent] LLM 调用失败，终止循环")
                return self._build_result(iteration + 1)

            message = response.choices[0].message

            # 将 assistant 消息追加到历史（包含 tool_calls 或纯文本）
            messages.append(self._message_to_dict(message))

            # 无 tool_calls → LLM 准备给出最终回答
            if not message.tool_calls:
                logger.info(f"[agent] LLM 给出最终回答（迭代 {iteration + 1}）")
                return self._build_result(
                    iteration + 1,
                    final_message=message.content,
                )

            # 执行所有 tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    logger.warning(f"[agent] 工具参数解析失败: {tool_call.function.arguments}")
                    tool_args = {}

                logger.info(f"[agent] 调用工具: {tool_name}({self._brief_args(tool_args)})")

                result_str = await self.tool_executor.execute(tool_name, tool_args)

                # 追加 tool result 消息
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str,
                    }
                )

        # 达到最大迭代，追加提示让 LLM 基于已有结果回答
        logger.warning(f"[agent] 达到最大迭代 {MAX_ITERATIONS}，强制生成回答")
        messages.append(
            {
                "role": "user",
                "content": "你已达到最大工具调用次数。请基于已收集的信息直接生成最终回答。如果没有任何搜索结果，请告知用户未找到相关信息。",
            }
        )

        try:
            response = await self._call_llm(messages, tools=None)
            if response:
                final_content = response.choices[0].message.content
            else:
                final_content = None
        except Exception as e:
            logger.error(f"[agent] 强制回答失败: {e}")
            final_content = None

        return self._build_result(MAX_ITERATIONS, final_message=final_content)

    # ---- 内部方法 ----

    def _build_initial_messages(
        self,
        query: str,
        search_query: str,
        intent_parsed: dict[str, Any],
        conversation_history: list[dict],
    ) -> list[dict]:
        """构建初始消息列表。"""
        # 意图上下文
        intent_parts = []
        if intent_parsed.get("keywords"):
            intent_parts.append(f"关键词: {', '.join(intent_parsed['keywords'])}")
        if intent_parsed.get("time_range") is not None:
            intent_parts.append(f"时间范围: 最近 {intent_parsed['time_range']} 天")
        if intent_parsed.get("confidence"):
            intent_parts.append(f"置信度: {intent_parsed['confidence']:.1%}")
        intent_context = "\n".join(intent_parts) if intent_parts else "（无特殊意图）"

        # 对话历史上下文
        conversation_context = ""
        if conversation_history:
            recent = conversation_history[-6:]  # 最近 3 轮（6 条消息）
            parts = []
            for msg in recent:
                role = "用户" if msg.get("role") == "user" else "助手"
                content = msg.get("content", "")[:200]
                parts.append(f"{role}: {content}")
            conversation_context = "\n".join(parts)

        system_prompt = AGENT_SYSTEM_PROMPT.format(
            intent_context=intent_context,
            conversation_context=conversation_context,
            max_iterations=MAX_ITERATIONS,
        )

        # 用户消息：优先使用改写后的查询
        user_content = search_query if search_query != query else query
        if search_query != query:
            user_content = (
                f"原始查询: {query}\n改写后查询: {search_query}\n\n请基于改写后的查询进行检索。"
            )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    async def _call_llm(self, messages: list[dict], tools: list | None = "default") -> Any:
        """调用 LLM（同步客户端在线程池中执行）。"""
        try:
            kwargs = {
                "model": get_llm_model(),
                "messages": messages,
                "temperature": 0.3,
            }
            if tools == "default":
                kwargs["tools"] = TOOL_SCHEMAS
                kwargs["tool_choice"] = "auto"
            elif tools is not None:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            loop = asyncio.get_event_loop()

            def _do_call():
                return client_llm.chat.completions.create(**kwargs)

            return await loop.run_in_executor(None, _do_call)

        except Exception as e:
            logger.error(f"[agent] LLM 调用失败: {type(e).__name__}: {e}", exc_info=True)
            return None

    def _build_result(self, iterations_used: int, final_message: str | None = None) -> AgentResult:
        """从 tool_executor 的累积结果构建 AgentResult。"""
        summaries = self.tool_executor.get_all_results()
        return AgentResult(
            summaries=summaries,
            iterations_used=iterations_used,
            final_message=final_message,
            has_results=len(summaries) > 0,
        )

    @staticmethod
    def _message_to_dict(message) -> dict:
        """将 OpenAI Message 对象转为 dict（保留 tool_calls）。"""
        d = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            d["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        return d

    @staticmethod
    def _brief_args(args: dict, max_len: int = 80) -> str:
        """生成简短的参数描述，用于日志。"""
        s = json.dumps(args, ensure_ascii=False)
        return s[:max_len] + "..." if len(s) > max_len else s

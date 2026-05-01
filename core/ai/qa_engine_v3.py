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
问答引擎 v3.2.0 - Agentic RAG + 向量搜索 + 多轮对话
"""

import asyncio
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from core.ai.agent_tools import TOOL_SCHEMAS, ToolExecutor
from core.ai.ai_client import client_llm
from core.ai.memory_manager import get_memory_manager
from core.ai.reranker import get_reranker
from core.ai.vector_store import get_vector_store
from core.config import get_qa_bot_persona
from core.infrastructure.database import get_db_manager
from core.settings import get_llm_model

from .conversation_manager import get_conversation_manager
from .intent_parser import get_intent_parser

logger = logging.getLogger(__name__)

# 系统提示词模板（使用占位符，人格描述会动态注入）
BASE_SYSTEM_TEMPLATE = """{persona_description}

---

## 核心任务
你是一个智能问答助手，负责根据频道历史总结回答用户问题。

## 核心约束（必须严格遵守）
1. **基于事实**：严格基于提供的历史总结内容回答，不要编造信息
2. **上下文理解**：如果有对话历史，优先利用上下文理解代词指代（如"它"、"那个"、"这个"等）
3. **明确回答**：总结中没有相关信息时，明确说明
4. **结构清晰**：使用清晰的结构和要点，语言简洁专业
5. **引用来源**：如果上下文或工具结果中提供了 post_links，请在相关要点后引用帖子链接
6. **Markdown规范**：
   - 粗体：使用 **文本** （两边各两个星号）
   - 斜体：使用 *文本* （两边各一个星号）
   - 代码：使用 `代码` （反引号）
   - **禁止使用 # 标题格式**
   - 列表：使用 - 或 • 开头
   - 链接：使用 [文本](URL) 格式
   - **禁止使用未配对的星号、下划线或反引号**

## 当前上下文
{channel_context}{conversation_context}

当前日期时间：{current_time}
"""

# Agentic RAG 最大工具调用迭代次数
AGENT_MAX_ITERATIONS = 10

# 追加到原系统提示词的工具使用说明
AGENT_TOOL_INSTRUCTIONS = """

## 搜索工具
你可以调用以下工具搜索频道历史总结来辅助回答：
- **semantic_search**: 语义搜索，适合模糊/概念性查询
- **keyword_search**: 关键词搜索，适合精确匹配特定术语
- **rerank_results**: 对搜索结果重排序（结果>5条时考虑使用）
- **list_channels**: 获取所有可查询频道链接
- **resolve_channel**: 将频道名、@username 或链接解析为标准频道链接
- **get_recent_summaries**: 获取最近总结，适合回答最新动态
- **get_channel_stats**: 获取频道统计信息
- **get_source_detail**: 展开之前搜索结果的完整来源内容

### 使用策略
1. 分析用户问题，确定需要的搜索方式和参数
2. 如果用户询问可用频道或频道链接，优先调用 list_channels
3. 如果用户指定频道名、@username 或频道链接，先调用 resolve_channel，再把 channel_id 传给搜索工具
4. 可以同时调用多个搜索工具（如语义+关键词并行检索）
5. 评估搜索结果：结果充足则回答，不足则调整参数再次搜索
6. 如果工具结果包含 post_links，最终回答必须尽量保留相关帖子链接作为证据来源
7. 最多进行{max_iterations}轮工具调用
"""


class QAEngineV3:
    """问答引擎 v3.2.0 - Agentic RAG + 向量搜索 + 多轮对话"""

    def __init__(self):
        """初始化问答引擎"""
        self.db = get_db_manager()
        self.intent_parser = get_intent_parser()
        self.memory_manager = get_memory_manager()
        self.vector_store = get_vector_store()
        self.reranker = get_reranker()
        self.conversation_mgr = get_conversation_manager()
        self.tool_executor = ToolExecutor(self.vector_store, self.memory_manager, self.reranker)
        logger.info("问答引擎v3.2.0初始化完成（Agentic RAG + 多轮对话）")

    async def process_query(self, query: str, user_id: int) -> str:
        """
        处理用户查询（支持多轮对话）

        Args:
            query: 用户查询
            user_id: 用户ID

        Returns:
            回答文本
        """
        try:
            logger.info(f"处理查询: user_id={user_id}, query={query}")

            # 1. 获取或创建会话
            session_id, is_new_session = self.conversation_mgr.get_or_create_session(user_id)

            # 2. 保存用户消息
            await self.conversation_mgr.save_message(
                user_id=user_id, session_id=session_id, role="user", content=query
            )

            # 3. 解析查询意图
            parsed = self.intent_parser.parse_query(query)
            logger.info(f"查询意图: {parsed['intent']}, 置信度: {parsed['confidence']}")

            # 4. 根据意图处理
            intent = parsed["intent"]

            if intent == "status":
                answer = await self._handle_status_query()
            elif intent == "stats":
                answer = await self._handle_stats_query(parsed)
            else:
                answer = await self._handle_content_query_v3(
                    parsed, user_id, session_id, is_new_session
                )

            # 5. 保存助手回复
            await self.conversation_mgr.save_message(
                user_id=user_id, session_id=session_id, role="assistant", content=answer
            )

            return answer

        except Exception as e:
            logger.error(f"处理查询失败: {type(e).__name__}: {e}", exc_info=True)
            return "❌ 处理查询时出错，请稍后重试。"

    async def _handle_status_query(self) -> str:
        """处理状态查询"""
        from core.ai.quota_manager import get_quota_manager

        quota_mgr = get_quota_manager()
        status = quota_mgr.get_system_status()

        vector_stats = self.vector_store.get_stats() if self.vector_store.is_available() else {}

        vector_info = ""
        if vector_stats.get("available"):
            summaries_count = vector_stats.get("summaries", {}).get("total_vectors", 0)
            messages_count = vector_stats.get("messages", {}).get("total_vectors", 0)
            vector_info = f"\n• 向量总结数: {summaries_count} 条"
            vector_info += f"\n• 向量消息数: {messages_count} 条"

        return f"""📊 系统状态

• 每日总限额: {status["daily_limit"]} 次
• 今日剩余: {status["remaining"]} 次{vector_info}

💡 每日00:00自动重置"""

    async def _handle_stats_query(self, parsed: dict[str, Any]) -> str:
        """处理统计查询"""
        stats = self.db.get_statistics()

        return f"""📈 数据统计

• 总总结数: {stats["total_count"]} 条
• 总消息数: {stats["total_messages"]:,} 条
• 平均消息数: {stats["avg_messages"]} 条/总结
• 本周总结: {stats["week_count"]} 条
• 本月总结: {stats["month_count"]} 条

📊 类型分布:""" + "\n".join(f"  • {t}: {c} 条" for t, c in stats.get("type_stats", {}).items())

    async def _handle_content_query_v3(
        self, parsed: dict[str, Any], user_id: int, session_id: str, is_new_session: bool = False
    ) -> str:
        """
        处理内容查询（v3.1.0）

        实现混合检索策略：
        1. 查询改写（多轮对话中含代词时）
        2. 语义检索（Dense，含时间过滤）
        3. 关键词检索（Sparse）作为补充
        4. RRF融合
        5. Reranker精排
        6. RAG生成（含对话历史）
        """
        try:
            query = parsed["original_query"]
            keywords = parsed.get("keywords", [])
            time_range = parsed.get("time_range")  # 可能为 None
            channel_id = await self._resolve_channel_from_parsed(parsed)

            # 获取对话历史
            conversation_history = await self.conversation_mgr.get_conversation_history(
                user_id, session_id
            )
            logger.debug(f"用户 {user_id} 的对话历史: {len(conversation_history)} 条")

            # ── 步骤1: 计算时间过滤范围 ─────────────────────────────────────────
            date_after: str | None = None
            if time_range is not None:
                cutoff = datetime.now(UTC) - timedelta(days=time_range)
                date_after = cutoff.isoformat()
                logger.info(f"时间过滤: date_after={date_after[:10]}")

            # ── 步骤2: 语义检索（双 collection: summaries + messages） ─────────────
            semantic_results = []
            if self.vector_store.is_available():
                try:
                    # 优先使用双 collection 联合检索
                    if self.vector_store.is_messages_available():
                        semantic_results = self.vector_store.search_all(
                            query=query,
                            top_k=20,
                            filter_metadata={"channel_id": channel_id} if channel_id else None,
                            date_after=date_after,
                        )
                        logger.info(f"双collection语义检索: 找到 {len(semantic_results)} 条结果")
                    else:
                        semantic_results = self.vector_store.search_similar(
                            query=query,
                            top_k=20,
                            filter_metadata={"channel_id": channel_id} if channel_id else None,
                            date_after=date_after,
                        )
                        logger.info(f"语义检索(summaries): 找到 {len(semantic_results)} 条结果")
                except Exception as e:
                    logger.error(f"语义检索失败: {e}")

            # ── 步骤3: 关键词检索（补充方案） ────────────────────────────────────
            keyword_results = []
            # 当语义检索结果不足或有明确关键词时，启用关键词检索
            if keywords or len(semantic_results) < 5:
                try:
                    search_days = time_range if time_range is not None else 90
                    keyword_results = await self.memory_manager.search_summaries(
                        keywords=keywords,
                        time_range_days=search_days,
                        channel_id=channel_id,
                        limit=10,
                    )
                    logger.info(f"关键词检索: 找到 {len(keyword_results)} 条结果")
                except Exception as e:
                    logger.error(f"关键词检索失败: {e}")

            # ── 步骤4: 融合结果 ───────────────────────────────────────────────────
            if semantic_results and keyword_results:
                final_candidates = self._rrf_fusion(semantic_results, keyword_results)
                logger.info(f"RRF融合: {len(final_candidates)} 条结果")
            elif semantic_results:
                final_candidates = semantic_results
            elif keyword_results:
                final_candidates = [
                    {
                        "summary_id": r["id"],
                        "summary_text": r["summary_text"],
                        "metadata": {
                            "channel_id": r.get("channel_id"),
                            "channel_name": r.get("channel_name"),
                            "created_at": r.get("created_at"),
                        },
                    }
                    for r in keyword_results
                ]
            else:
                if time_range is not None and time_range <= 7:
                    return (
                        f"🔍 在最近 {time_range} 天内未找到相关总结。\n\n"
                        f"💡 提示：可以尝试扩大时间范围，例如'最近30天关于...'。"
                    )
                return "🔍 未找到相关总结。\n\n💡 提示：尝试调整关键词或时间范围。"

            # ── 步骤5: 重排序（Top-20 → Top-5） ─────────────────────────────────
            if self.reranker.is_available() and len(final_candidates) > 5:
                try:
                    final_candidates = self.reranker.rerank(query, final_candidates, top_k=5)
                    logger.info(f"重排序完成: 保留 {len(final_candidates)} 条结果")
                except Exception as e:
                    logger.error(f"重排序失败: {e}")
                    final_candidates = final_candidates[:5]
            else:
                final_candidates = final_candidates[:5]

            # ── 步骤6: AI生成回答（RAG + 对话历史） ──────────────────────────────
            answer = await self._generate_answer_with_rag(
                query=query,
                summaries=final_candidates,
                keywords=keywords,
                conversation_history=conversation_history,
            )

            # 新会话时加上引导语
            if is_new_session:
                answer = "🍃 *开始新的对话。*\n\n" + answer

            return answer

        except Exception as e:
            logger.error(f"处理内容查询失败: {type(e).__name__}: {e}", exc_info=True)
            return "❌ 查询失败，请稍后重试。"

    def _rrf_fusion(
        self, semantic_results: list[dict], keyword_results: list[dict], k: int = 60
    ) -> list[dict]:
        """
        Reciprocal Rank Fusion (RRF) 融合算法

        Args:
            semantic_results: 语义检索结果
            keyword_results: 关键词检索结果
            k: RRF常数，默认60

        Returns:
            融合后的结果列表
        """
        result_map = {}

        # 处理语义检索结果
        for rank, result in enumerate(semantic_results, 1):
            summary_id = result["summary_id"]
            score = 1.0 / (k + rank)
            result_map[summary_id] = {"summary": result, "score": score, "source": "semantic"}

        # 处理关键词检索结果
        for rank, result in enumerate(keyword_results, 1):
            summary_id = result["id"]
            score = 1.0 / (k + rank)

            if summary_id in result_map:
                result_map[summary_id]["score"] += score
                result_map[summary_id]["source"] = "hybrid"
            else:
                result_map[summary_id] = {
                    "summary": {
                        "summary_id": result["id"],
                        "summary_text": result["summary_text"],
                        "metadata": {
                            "channel_id": result.get("channel_id"),
                            "channel_name": result.get("channel_name"),
                            "created_at": result.get("created_at"),
                        },
                    },
                    "score": score,
                    "source": "keyword",
                }

        sorted_results = sorted(result_map.values(), key=lambda x: x["score"], reverse=True)

        return [item["summary"] for item in sorted_results]

    async def _build_rag_prompts(
        self,
        query: str,
        summaries: list[dict[str, Any]],
        keywords: list[str] = None,
        conversation_history: list[dict] = None,
    ) -> tuple:
        """构建 RAG 所需的 system_prompt 和 user_prompt（降级路径使用）"""
        context = self._prepare_rag_context(summaries)

        channel_ids = list(
            set(
                s.get("metadata", {}).get("channel_id") or s.get("channel_id", "")
                for s in summaries
            )
        )
        channel_context = ""
        if len(channel_ids) == 1 and channel_ids[0]:
            channel_context = await self.memory_manager.get_channel_context(channel_ids[0])
        elif len(channel_ids) > 1:
            channel_context = "多频道综合查询"

        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            history_excluding_current = (
                conversation_history[:-1] if len(conversation_history) > 1 else []
            )
            if history_excluding_current:
                conversation_context = self.conversation_mgr.format_conversation_context(
                    history_excluding_current
                )
                conversation_context = f"\n【对话历史】\n{conversation_context}\n"

        persona_description = get_qa_bot_persona()
        current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M") + " (UTC)"
        system_prompt = BASE_SYSTEM_TEMPLATE.format(
            persona_description=persona_description,
            channel_context=channel_context,
            conversation_context=conversation_context,
            current_time=current_time,
        )

        user_prompt = (
            f"用户当前查询：{query}\n\n"
            f"相关历史总结（共{len(summaries)}条，已通过语义搜索和重排序精选）：\n"
            f"{context}\n\n"
            f"请根据上述总结回答用户的问题。"
        )

        return system_prompt, user_prompt

    async def _generate_answer_with_rag(
        self,
        query: str,
        summaries: list[dict[str, Any]],
        keywords: list[str] = None,
        conversation_history: list[dict] = None,
    ) -> str:
        """使用RAG生成回答（降级路径使用）"""
        try:
            system_prompt, user_prompt = await self._build_rag_prompts(
                query=query,
                summaries=summaries,
                keywords=keywords,
                conversation_history=conversation_history,
            )

            logger.info(
                f"调用AI生成回答（RAG+对话历史），总结数: {len(summaries)}, "
                f"历史消息: {len(conversation_history) if conversation_history else 0}"
            )

            response = client_llm.chat.completions.create(
                model=get_llm_model(),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"AI回答生成成功，长度: {len(answer)}字符")

            # 添加来源信息（若AI已自行生成来源块则不重复追加）
            if "📚 数据来源" not in answer:
                source_info = self._format_source_info_v3(summaries)
                return f"{answer}\n\n{source_info}"
            return answer

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            logger.error(f"AI生成回答失败: {error_type}: {error_msg}", exc_info=True)

            if "Moderation Block" in error_msg or "content_filter" in error_msg:
                return """⚠️ **查询内容受限**

抱歉，你的查询触发了内容过滤机制，无法提供相关信息。

💡 **建议：**
• 询问频道里最近的总结
• 查询特定主题的历史记录
• 使用不同的关键词重新表述问题

请重新组织你的问题再试。"""

            return self._fallback_answer_v3(summaries)

    async def generate_answer_stream(
        self,
        query: str,
        summaries: list[dict[str, Any]],
        keywords: list[str] = None,
        conversation_history: list[dict] = None,
    ):
        """使用RAG流式生成回答（异步生成器，降级路径使用）"""
        import asyncio

        system_prompt, user_prompt = await self._build_rag_prompts(
            query=query,
            summaries=summaries,
            keywords=keywords,
            conversation_history=conversation_history,
        )

        logger.info(
            f"调用AI流式生成回答（RAG），总结数: {len(summaries)}, "
            f"历史消息: {len(conversation_history) if conversation_history else 0}"
        )

        loop = asyncio.get_event_loop()

        def _do_stream():
            return client_llm.chat.completions.create(
                model=get_llm_model(),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                stream=True,
            )

        # 在线程池中调用同步 SDK，避免阻塞事件循环
        stream = await loop.run_in_executor(None, _do_stream)

        full_text = ""
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
            if delta:
                full_text += delta
                yield delta

        # 追加来源信息
        if "📚 数据来源" not in full_text:
            source_info = self._format_source_info_v3(summaries)
            suffix = f"\n\n{source_info}"
            yield suffix

    async def process_query_stream(self, query: str, user_id: int, channel_hint: str | None = None):
        """
        流式处理用户查询（异步生成器版本）

        先完成检索/改写等预处理阶段，然后流式 yield AI 生成的文本。

        Yields:
            str: 文本片段，以 "__DONE__" 结尾表示完成，
                 以 "__ERROR__:<msg>" 表示出错，
                 以 "__NEW_SESSION__" 表示开始了新会话。
        """
        try:
            logger.info(f"[stream] 处理查询: user_id={user_id}, query={query}")

            # 1. 获取或创建会话
            session_id, is_new_session = self.conversation_mgr.get_or_create_session(user_id)

            # 2. 保存用户消息
            await self.conversation_mgr.save_message(
                user_id=user_id, session_id=session_id, role="user", content=query
            )

            # 3. 解析查询意图
            parsed = self.intent_parser.parse_query(query)
            if channel_hint:
                parsed["channel_hint"] = channel_hint
            intent = parsed["intent"]

            # 4. 非内容查询直接返回（不使用流式）
            if intent == "status":
                answer = await self._handle_status_query()
                yield answer
                await self.conversation_mgr.save_message(
                    user_id=user_id, session_id=session_id, role="assistant", content=answer
                )
                yield "__DONE__"
                return

            if intent == "stats":
                answer = await self._handle_stats_query(parsed)
                yield answer
                await self.conversation_mgr.save_message(
                    user_id=user_id, session_id=session_id, role="assistant", content=answer
                )
                yield "__DONE__"
                return

            # 5. 内容查询：先完成检索阶段，再流式生成
            if is_new_session:
                yield "__NEW_SESSION__"

            original_query = parsed["original_query"]
            keywords = parsed.get("keywords", [])
            time_range = parsed.get("time_range")
            # 这里预解析频道用于约束首轮检索与降级流水线；即使 agentic 模式后续
            # 自主调用 resolve_channel，也可以确保向量检索从一开始就限定频道。
            channel_id = await self._resolve_channel_from_parsed(parsed)

            conversation_history = await self.conversation_mgr.get_conversation_history(
                user_id, session_id
            )

            # 时间过滤
            date_after: str | None = None
            if time_range is not None:
                cutoff = datetime.now(UTC) - timedelta(days=time_range)
                date_after = cutoff.isoformat()

            # Agentic RAG：LLM 自主决定是否检索
            full_answer = ""
            try:
                async for chunk in self._agentic_stream(
                    query=original_query,
                    conversation_history=conversation_history,
                    time_range=time_range,
                    date_after=date_after,
                    keywords=keywords,
                    channel_id=channel_id,
                    channel_hint=parsed.get("channel_hint"),
                ):
                    full_answer += chunk
                    yield chunk

            except Exception as e:
                logger.error(f"[stream] Agentic 处理异常，降级到固定流水线: {e}", exc_info=True)
                final_candidates = await self._fallback_fixed_pipeline(
                    search_query=original_query,
                    keywords=keywords,
                    time_range=time_range,
                    date_after=date_after,
                    channel_id=channel_id,
                )
                if final_candidates:
                    async for chunk in self.generate_answer_stream(
                        query=original_query,
                        summaries=final_candidates,
                        keywords=keywords,
                        conversation_history=conversation_history,
                    ):
                        full_answer += chunk
                        yield chunk
                else:
                    if time_range is not None and time_range <= 7:
                        full_answer = (
                            f"🔍 在最近 {time_range} 天内未找到相关总结。\n\n"
                            f"💡 提示：可以尝试扩大时间范围，例如'最近30天关于...'。"
                        )
                    else:
                        full_answer = "🔍 未找到相关总结。\n\n💡 提示：尝试调整关键词或时间范围。"
                    yield full_answer

            # 保存完整回答到对话历史
            if is_new_session:
                full_answer = "🍃 *开始新的对话。*\n\n" + full_answer
            await self.conversation_mgr.save_message(
                user_id=user_id, session_id=session_id, role="assistant", content=full_answer
            )

            yield "__DONE__"

        except Exception as e:
            logger.error(f"[stream] 处理查询失败: {type(e).__name__}: {e}", exc_info=True)
            yield "__ERROR__:❌ 处理查询时出错，请稍后重试。"

    def _prepare_rag_context(self, summaries: list[dict[str, Any]]) -> str:
        """
        准备RAG上下文信息

        动态分配每条总结的最大字符数：
        - 1条结果: 最多 2000 字符
        - 2条结果: 最多 1500 字符
        - 3-4条结果: 最多 1000 字符
        - 5条结果: 最多 800 字符
        """
        count = len(summaries[:5])
        if count <= 1:
            max_chars = 2000
        elif count == 2:
            max_chars = 1500
        elif count <= 4:
            max_chars = 1000
        else:
            max_chars = 800

        context_parts = []
        for i, summary in enumerate(summaries[:5], 1):
            metadata = summary.get("metadata", {})
            channel_name = metadata.get("channel_name") or summary.get("channel_name", "未知频道")
            created_at = metadata.get("created_at") or summary.get("created_at", "")
            summary_text = summary.get("summary_text", "")
            post_links = self._extract_post_links(summary)

            # 来源标签（总结 or 原始消息）
            source_tag = ""
            if summary.get("source") == "message":
                source_tag = " [消息]"
            elif summary.get("source") == "summary":
                source_tag = " [总结]"

            # 动态截断
            text_preview = (
                summary_text[:max_chars] + "..." if len(summary_text) > max_chars else summary_text
            )

            # 分数信息
            score_info = ""
            if "similarity" in summary:
                score_info = f" [相似度: {summary['similarity']:.2f}]"
            if "rerank_score" in summary:
                score_info += f" [重排分: {summary['rerank_score']:.2f}]"

            links_text = ""
            if post_links:
                links_text = "\n相关帖子链接: " + " ".join(post_links[:5])

            context_parts.append(
                f"[{i}] {channel_name} ({created_at}){source_tag}{score_info}\n"
                f"{text_preview}{links_text}"
            )

        return "\n\n".join(context_parts)

    def _format_source_info_v3(self, summaries: list[dict[str, Any]]) -> str:
        """格式化来源信息（v3版本）"""
        channels = {}
        post_links = []
        for s in summaries:
            metadata = s.get("metadata", {})
            channel_id = metadata.get("channel_id") or s.get("channel_id", "")
            channel_name = metadata.get("channel_name") or s.get("channel_name", "未知频道")
            for link in self._extract_post_links(s):
                if link not in post_links:
                    post_links.append(link)

            if channel_id not in channels:
                channels[channel_id] = {"name": channel_name, "count": 0}
            channels[channel_id]["count"] += 1

        sources = [f"• {info['name']}: {info['count']}条" for info in channels.values()]

        source_text = f"📚 数据来源: {len(sources)}个频道\n" + "\n".join(sources)
        if post_links:
            source_text += "\n🔗 相关帖子: " + " ".join(post_links[:5])
        return source_text

    @staticmethod
    def _extract_post_links(summary: dict[str, Any]) -> list[str]:
        """从结果中提取帖子链接，保证 RAG 上下文和来源信息使用同一逻辑。"""
        metadata = summary.get("metadata", {})
        links = summary.get("post_links") or metadata.get("post_links") or []
        if isinstance(links, str):
            return [links]
        return list(links)

    async def _resolve_channel_from_parsed(self, parsed: dict[str, Any]) -> str | None:
        """根据解析结果获取标准频道 ID。"""
        channel_id = parsed.get("channel_id")
        if channel_id:
            return channel_id

        channel_hint = parsed.get("channel_hint")
        if not channel_hint:
            return None

        resolved = await self.memory_manager.resolve_channel(channel_hint)
        if resolved.get("success"):
            return resolved.get("channel_id")

        logger.info(f"频道提示未能唯一解析: {channel_hint}, result={resolved}")
        return None

    async def _agentic_stream(
        self,
        query: str,
        conversation_history: list[dict],
        time_range: int | None,
        date_after: str | None,
        keywords: list[str],
        channel_id: str | None = None,
        channel_hint: str | None = None,
    ):
        """Agentic RAG 流式生成器。Tool-calling 循环（非流式）+ 最终回答（流式）。"""
        self.tool_executor.reset()
        loop = asyncio.get_running_loop()

        # 构建系统提示词：原有提示词 + 工具说明
        channel_context = await self.memory_manager.get_channel_context()
        conversation_context = self.conversation_mgr.format_conversation_context(
            conversation_history
        )
        persona_description = get_qa_bot_persona()

        current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M") + " (UTC)"
        system_prompt = BASE_SYSTEM_TEMPLATE.format(
            persona_description=persona_description,
            channel_context=channel_context,
            conversation_context=conversation_context,
            current_time=current_time,
        )
        system_prompt += AGENT_TOOL_INSTRUCTIONS.format(max_iterations=AGENT_MAX_ITERATIONS)

        # 意图上下文
        intent_parts = []
        if keywords:
            intent_parts.append(f"系统分析的关键词: {', '.join(keywords)}")
        if time_range is not None:
            intent_parts.append(f"系统分析的时间范围: 最近 {time_range} 天")
        if date_after:
            intent_parts.append(f"时间过滤起点: {date_after}")
        if channel_hint:
            intent_parts.append(f"用户指定的频道提示: {channel_hint}")
        if channel_id:
            intent_parts.append(f"已解析频道ID: {channel_id}")
            intent_parts.append("后续检索必须优先带上该 channel_id 过滤。")

        intent_note = "\n".join(intent_parts) if intent_parts else ""
        user_content = query
        if intent_note:
            user_content += f"\n\n{intent_note}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # Tool-calling 循环（非流式）
        for iteration in range(AGENT_MAX_ITERATIONS):
            logger.info(f"[agent] 迭代 {iteration + 1}/{AGENT_MAX_ITERATIONS}")

            response = await loop.run_in_executor(
                None,
                lambda: client_llm.chat.completions.create(
                    model=get_llm_model(),
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                    temperature=0.7,
                ),
            )

            if not response or not response.choices:
                logger.warning("[agent] LLM 返回无效响应")
                return

            message = response.choices[0].message
            messages.append(self._message_to_dict(message))

            # 无 tool_calls → LLM 准备回答，切换到流式
            if not message.tool_calls:
                logger.info(f"[agent] LLM 就绪（迭代 {iteration + 1}），开始流式生成")
                break

            # 执行 tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    logger.warning(f"[agent] 工具参数解析失败: {tool_call.function.arguments}")
                    tool_args = {}

                logger.info(f"[agent] 调用工具: {tool_name}")
                result_str = await self.tool_executor.execute(tool_name, tool_args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str,
                    }
                )
        else:
            # 达到最大迭代，追加提示
            logger.warning(f"[agent] 达到最大迭代 {AGENT_MAX_ITERATIONS}，强制生成回答")
            messages.append(
                {
                    "role": "user",
                    "content": "请基于已收集的信息直接生成最终回答。",
                }
            )

        # 流式生成最终回答
        stream = await loop.run_in_executor(
            None,
            lambda: client_llm.chat.completions.create(
                model=get_llm_model(),
                messages=messages,
                temperature=0.7,
                stream=True,
            ),
        )

        full_text = ""
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full_text += delta
                yield delta

        # 追加来源信息
        all_results = self.tool_executor.get_all_results()
        if all_results and "📚 数据来源" not in full_text:
            source_info = self._format_source_info_v3(all_results)
            yield f"\n\n{source_info}"

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

    async def _fallback_fixed_pipeline(
        self,
        search_query: str,
        keywords: list[str],
        time_range: int | None,
        date_after: str | None,
        channel_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """降级到固定流水线（当 Agentic 处理异常时使用）。"""
        logger.info("[fallback] 使用固定流水线检索")

        # 语义检索
        semantic_results = []
        if self.vector_store.is_available():
            try:
                semantic_results = self.vector_store.search_similar(
                    query=search_query,
                    top_k=20,
                    filter_metadata={"channel_id": channel_id} if channel_id else None,
                    date_after=date_after,
                )
            except Exception as e:
                logger.error(f"[fallback] 语义检索失败: {e}")

        # 关键词检索
        keyword_results = []
        if keywords or len(semantic_results) < 5:
            try:
                search_days = time_range if time_range is not None else 90
                keyword_results = await self.memory_manager.search_summaries(
                    keywords=keywords,
                    time_range_days=search_days,
                    channel_id=channel_id,
                    limit=10,
                )
            except Exception as e:
                logger.error(f"[fallback] 关键词检索失败: {e}")

        # 融合
        if semantic_results and keyword_results:
            final_candidates = self._rrf_fusion(semantic_results, keyword_results)
        elif semantic_results:
            final_candidates = semantic_results
        elif keyword_results:
            final_candidates = [
                {
                    "summary_id": r["id"],
                    "summary_text": r["summary_text"],
                    "metadata": {
                        "channel_id": r.get("channel_id"),
                        "channel_name": r.get("channel_name"),
                        "created_at": r.get("created_at"),
                    },
                }
                for r in keyword_results
            ]
        else:
            return []

        # 重排序
        if self.reranker.is_available() and len(final_candidates) > 5:
            try:
                final_candidates = self.reranker.rerank(search_query, final_candidates, top_k=5)
            except Exception as e:
                logger.error(f"[fallback] 重排序失败: {e}")
                final_candidates = final_candidates[:5]
        else:
            final_candidates = final_candidates[:5]

        return final_candidates

    def _fallback_answer_v3(self, summaries: list[dict[str, Any]]) -> str:
        """降级方案：直接返回总结摘要（v3版本）"""
        result = "📋 相关总结摘要：\n\n"

        for i, summary in enumerate(summaries[:3], 1):
            metadata = summary.get("metadata", {})
            channel_name = metadata.get("channel_name") or summary.get("channel_name", "未知频道")
            created_at_raw = metadata.get("created_at") or summary.get("created_at", "")
            created_at = (
                created_at_raw.strftime("%Y-%m-%d")
                if hasattr(created_at_raw, "strftime")
                else str(created_at_raw)
            )[:10]
            text = summary.get("summary_text", "")[:300]

            result += f"{i}. **{channel_name}** ({created_at})\n{text}...\n\n"

        return result


# 创建全局问答引擎v3实例
qa_engine_v3 = None


def get_qa_engine_v3():
    """获取全局问答引擎v3实例"""
    global qa_engine_v3
    if qa_engine_v3 is None:
        qa_engine_v3 = QAEngineV3()
    return qa_engine_v3

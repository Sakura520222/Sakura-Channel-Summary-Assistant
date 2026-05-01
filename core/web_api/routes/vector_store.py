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
向量存储管理 API 路由

提供向量存储（ChromaDB）的浏览、搜索、删除等管理功能。
"""

import logging

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_vector_stats():
    """获取向量存储统计信息

    Returns:
        向量存储统计数据，包含 summaries 和 messages 两个 collection 的信息
    """
    try:
        from core.ai.vector_store import get_vector_store

        vs = get_vector_store()
        stats = vs.get_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"获取向量存储统计失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/collections/{collection_name}")
async def list_collection_documents(
    collection_name: str,
    limit: int = Query(50, ge=1, le=200, description="返回数量上限"),
    offset: int = Query(0, ge=0, description="偏移量"),
):
    """列出指定 collection 中的文档

    Args:
        collection_name: 集合名称（summaries 或 messages）

    Returns:
        文档列表和总数
    """
    if collection_name not in ("summaries", "messages"):
        raise HTTPException(status_code=400, detail=f"不支持的集合名称: {collection_name}")

    try:
        from core.ai.vector_store import get_vector_store

        vs = get_vector_store()
        collection = vs.collection if collection_name == "summaries" else vs.messages_collection

        if collection is None:
            return {
                "success": True,
                "data": {"documents": [], "total": 0, "available": False},
            }

        total = collection.count()
        if total == 0:
            return {"success": True, "data": {"documents": [], "total": 0, "available": True}}

        # 限制查询范围
        fetch_limit = min(limit, total)
        actual_offset = min(offset, max(total - 1, 0))

        results = collection.get(
            include=["metadatas", "documents"],
            limit=fetch_limit,
            offset=actual_offset,
        )

        documents = []
        if results and results["ids"]:
            for i, doc_id in enumerate(results["ids"]):
                doc = {
                    "id": doc_id,
                    "document": (results["documents"] or [None])[i] or "",
                    "metadata": (results["metadatas"] or [{}])[i] or {},
                }
                documents.append(doc)

        return {
            "success": True,
            "data": {
                "documents": documents,
                "total": total,
                "limit": fetch_limit,
                "offset": actual_offset,
                "available": True,
            },
        }

    except Exception as e:
        logger.error(f"列出 collection 文档失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/collections/{collection_name}/{doc_id}")
async def get_document(collection_name: str, doc_id: str):
    """获取指定文档的详细信息

    Args:
        collection_name: 集合名称（summaries 或 messages）
        doc_id: 文档 ID

    Returns:
        文档详细信息
    """
    if collection_name not in ("summaries", "messages"):
        raise HTTPException(status_code=400, detail=f"不支持的集合名称: {collection_name}")

    try:
        from core.ai.vector_store import get_vector_store

        vs = get_vector_store()
        collection = vs.collection if collection_name == "summaries" else vs.messages_collection

        if collection is None:
            raise HTTPException(status_code=503, detail="向量存储不可用")

        results = collection.get(ids=[doc_id], include=["metadatas", "documents", "embeddings"])

        if not results["ids"]:
            raise HTTPException(status_code=404, detail=f"文档不存在: {doc_id}")

        doc = {
            "id": results["ids"][0],
            "document": (results["documents"] or [None])[0] or "",
            "metadata": (results["metadatas"] or [{}])[0] or {},
            "embedding_dimension": None,
        }

        # 计算向量维度（不返回完整向量数据以节省带宽）
        embeddings = results.get("embeddings")
        if embeddings is not None and len(embeddings) > 0 and embeddings[0] is not None:
            doc["embedding_dimension"] = len(embeddings[0])

        return {"success": True, "data": doc}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档详情失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/collections/{collection_name}/{doc_id}")
async def delete_document(collection_name: str, doc_id: str):
    """删除指定文档

    Args:
        collection_name: 集合名称（summaries 或 messages）
        doc_id: 文档 ID

    Returns:
        删除结果
    """
    if collection_name not in ("summaries", "messages"):
        raise HTTPException(status_code=400, detail=f"不支持的集合名称: {collection_name}")

    try:
        from core.ai.vector_store import get_vector_store

        vs = get_vector_store()

        if collection_name == "summaries":
            success = vs.delete_summary(int(doc_id))
        else:
            success = vs.delete_message(doc_id)

        if success:
            logger.info(f"已删除向量文档: {collection_name}/{doc_id}")
            return {"success": True, "message": f"已删除文档: {doc_id}"}
        else:
            return {"success": False, "message": f"删除文档失败: {doc_id}"}

    except Exception as e:
        logger.error(f"删除向量文档失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/collections/{collection_name}")
async def delete_documents_batch(
    collection_name: str,
    doc_ids: list[str],
):
    """批量删除文档

    Args:
        collection_name: 集合名称（summaries 或 messages）
        doc_ids: 要删除的文档 ID 列表

    Returns:
        批量删除结果
    """
    if collection_name not in ("summaries", "messages"):
        raise HTTPException(status_code=400, detail=f"不支持的集合名称: {collection_name}")

    try:
        from core.ai.vector_store import get_vector_store

        vs = get_vector_store()
        collection = vs.collection if collection_name == "summaries" else vs.messages_collection

        if collection is None:
            raise HTTPException(status_code=503, detail="向量存储不可用")

        collection.delete(ids=doc_ids)
        logger.info(f"批量删除向量文档: {collection_name}, 数量: {len(doc_ids)}")

        return {
            "success": True,
            "message": f"已删除 {len(doc_ids)} 个文档",
            "data": {"deleted_count": len(doc_ids)},
        }

    except Exception as e:
        logger.error(f"批量删除向量文档失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/search")
async def search_vectors(
    query: str = Query(..., description="搜索查询文本"),
    collection: str | None = Query(None, description="限定搜索集合 (summaries/messages/all)"),
    top_k: int = Query(10, ge=1, le=50, description="返回结果数量"),
):
    """搜索向量存储

    Args:
        query: 搜索查询文本
        collection: 限定搜索集合（summaries/messages/all），默认搜索全部
        top_k: 返回结果数量

    Returns:
        搜索结果列表
    """
    try:
        from core.ai.vector_store import get_vector_store

        vs = get_vector_store()

        if collection == "summaries":
            results = vs.search_similar(query=query, top_k=top_k)
        elif collection == "messages":
            results = vs.search_messages(query=query, top_k=top_k)
        else:
            results = vs.search_all(query=query, top_k=top_k)

        return {
            "success": True,
            "data": {
                "results": results,
                "total": len(results),
                "query": query,
            },
        }

    except Exception as e:
        logger.error(f"搜索向量失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/collections/{collection_name}/clear")
async def clear_collection(collection_name: str):
    """清空指定 collection 中的所有文档

    Args:
        collection_name: 集合名称（summaries 或 messages）

    Returns:
        清空结果
    """
    if collection_name not in ("summaries", "messages"):
        raise HTTPException(status_code=400, detail=f"不支持的集合名称: {collection_name}")

    try:
        from core.ai.vector_store import get_vector_store

        vs = get_vector_store()
        coll = vs.collection if collection_name == "summaries" else vs.messages_collection

        if coll is None:
            raise HTTPException(status_code=503, detail="向量存储不可用")

        count = coll.count()
        if count == 0:
            return {"success": True, "message": "集合已经是空的", "data": {"deleted_count": 0}}

        # 获取所有 ID 并批量删除
        all_docs = coll.get(include=[])
        if all_docs and all_docs["ids"]:
            coll.delete(ids=all_docs["ids"])

        logger.info(f"已清空向量集合: {collection_name}, 删除 {count} 条记录")
        return {
            "success": True,
            "message": f"已清空集合 {collection_name}（{count} 条记录）",
            "data": {"deleted_count": count},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清空向量集合失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e

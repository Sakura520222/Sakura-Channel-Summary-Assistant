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
AI 配置 API 路由

提供 AI 模型配置和提示词管理功能。
"""

import logging

import aiofiles
from fastapi import APIRouter, HTTPException

from core.config import DEFAULT_POLL_PROMPT, DEFAULT_PROMPT, DEFAULT_QA_PERSONA
from core.web_api.schemas.config import (
    AIConfigResponse,
    AIConfigUpdateRequest,
    PromptResponse,
    PromptUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# 提示词文件路径映射
PROMPT_FILES = {
    "summary": "data/prompt.txt",
    "poll": "data/poll_prompt.txt",
    "qa": "data/qa_persona.txt",
}

# 默认提示词
DEFAULT_PROMPTS = {
    "summary": DEFAULT_PROMPT,
    "poll": DEFAULT_POLL_PROMPT,
    "qa": DEFAULT_QA_PERSONA,
}


@router.get("/config")
async def get_ai_config():
    """获取 AI 配置信息"""
    try:
        from core.settings import get_settings

        settings = get_settings()

        api_key = settings.ai.effective_api_key
        api_key_preview = ""
        if api_key:
            api_key_preview = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"

        return {
            "success": True,
            "data": AIConfigResponse(
                base_url=settings.ai.base_url,
                model=settings.ai.model,
                api_key_set=bool(api_key),
                api_key_preview=api_key_preview,
            ).model_dump(),
        }
    except Exception as e:
        logger.error(f"获取 AI 配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/config")
async def update_ai_config(request: AIConfigUpdateRequest):
    """更新 AI 配置"""
    try:
        # 读取现有 .env
        env_path = "data/.env"
        env_lines: list[str] = []

        try:
            async with aiofiles.open(env_path, encoding="utf-8") as f:
                env_lines = await f.readlines()
        except FileNotFoundError:
            pass

        # 更新配置项
        updates = {}
        if request.base_url is not None:
            updates["LLM_BASE_URL"] = request.base_url
        if request.model is not None:
            updates["LLM_MODEL"] = request.model
        if request.api_key is not None:
            updates["LLM_API_KEY"] = request.api_key

        # 更新或添加配置行
        for key, value in updates.items():
            found = False
            for i, line in enumerate(env_lines):
                if line.strip().startswith(f"{key}="):
                    env_lines[i] = f"{key}={value}\n"
                    found = True
                    break
            if not found:
                env_lines.append(f"{key}={value}\n")

        # 写回 .env
        async with aiofiles.open(env_path, "w", encoding="utf-8") as f:
            await f.writelines(env_lines)

        # 重新加载 settings
        from core.settings import reload_settings

        reload_settings()

        logger.info("已通过 WebUI 更新 AI 配置")
        return {"success": True, "message": "AI 配置已更新，部分配置需要重启生效"}

    except Exception as e:
        logger.error(f"更新 AI 配置失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/prompts")
async def list_prompts():
    """获取所有提示词"""
    try:
        prompts = []
        for prompt_type, file_path in PROMPT_FILES.items():
            content = await _read_prompt_file(file_path)
            default_content = DEFAULT_PROMPTS.get(prompt_type, "")
            is_default = content == default_content if content else False

            prompts.append(
                PromptResponse(
                    prompt_type=prompt_type,
                    content=content,
                    is_default=is_default,
                ).model_dump()
            )

        return {"success": True, "data": prompts}

    except Exception as e:
        logger.error(f"获取提示词列表失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/prompts/{prompt_type}")
async def get_prompt(prompt_type: str):
    """获取指定类型的提示词"""
    if prompt_type not in PROMPT_FILES:
        raise HTTPException(status_code=400, detail=f"无效的提示词类型: {prompt_type}")

    try:
        file_path = PROMPT_FILES[prompt_type]
        content = await _read_prompt_file(file_path)
        default_content = DEFAULT_PROMPTS.get(prompt_type, "")
        is_default = content == default_content if content else False

        return {
            "success": True,
            "data": PromptResponse(
                prompt_type=prompt_type,
                content=content,
                is_default=is_default,
            ).model_dump(),
        }

    except Exception as e:
        logger.error(f"获取提示词失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/prompts/{prompt_type}")
async def update_prompt(prompt_type: str, request: PromptUpdateRequest):
    """更新指定类型的提示词"""
    if prompt_type not in PROMPT_FILES:
        raise HTTPException(status_code=400, detail=f"无效的提示词类型: {prompt_type}")

    try:
        file_path = PROMPT_FILES[prompt_type]
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(request.content)

        logger.info(f"已通过 WebUI 更新提示词: {prompt_type}")
        return {"success": True, "message": f"提示词已更新: {prompt_type}"}

    except Exception as e:
        logger.error(f"更新提示词失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/prompts/{prompt_type}/reset")
async def reset_prompt(prompt_type: str):
    """重置提示词为默认值"""
    if prompt_type not in PROMPT_FILES:
        raise HTTPException(status_code=400, detail=f"无效的提示词类型: {prompt_type}")

    try:
        file_path = PROMPT_FILES[prompt_type]
        default_content = DEFAULT_PROMPTS.get(prompt_type, "")

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(default_content)

        logger.info(f"已通过 WebUI 重置提示词: {prompt_type}")
        return {"success": True, "message": f"提示词已重置为默认值: {prompt_type}"}

    except Exception as e:
        logger.error(f"重置提示词失败: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


async def _read_prompt_file(file_path: str) -> str:
    """读取提示词文件内容"""
    try:
        async with aiofiles.open(file_path, encoding="utf-8") as f:
            return (await f.read()).strip()
    except FileNotFoundError:
        return ""

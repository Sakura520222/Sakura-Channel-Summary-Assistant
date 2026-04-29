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
JWT 认证模块

提供 JWT Token 生成、验证和 FastAPI 依赖注入功能。
Token 使用 Bot Token 的 SHA256 作为签名密钥，无需额外配置。
"""

import hashlib
import logging
import time
from dataclasses import dataclass

import jwt

logger = logging.getLogger(__name__)

# Token 有效期：7 天
TOKEN_EXPIRY_SECONDS = 7 * 24 * 3600

# 开发模式 Token
DEV_TOKEN = "dev"


@dataclass
class WebUIUser:
    """WebUI 认证用户"""

    user_id: str
    is_dev: bool = False


def _get_jwt_secret() -> str:
    """获取 JWT 签名密钥（基于 Bot Token 的 SHA256）"""
    from core.settings import get_settings

    settings = get_settings()
    bot_token = settings.telegram.bot_token or "sakura-bot-default-secret"
    return hashlib.sha256(f"webui:{bot_token}".encode()).hexdigest()


def generate_token(user_id: str) -> str:
    """生成 JWT Token

    Args:
        user_id: 用户标识（管理员 ID 或固定标识）

    Returns:
        str: JWT Token 字符串
    """
    secret = _get_jwt_secret()
    payload = {
        "sub": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS,
        "scope": "webui",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str) -> WebUIUser | None:
    """验证 JWT Token

    Args:
        token: JWT Token 字符串

    Returns:
        WebUIUser | None: 验证成功返回用户信息，失败返回 None
    """
    if not token:
        return None

    # 开发模式
    if token == DEV_TOKEN:
        return WebUIUser(user_id="dev", is_dev=True)

    try:
        secret = _get_jwt_secret()
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        if payload.get("scope") != "webui":
            return None
        return WebUIUser(user_id=payload["sub"])
    except jwt.ExpiredSignatureError:
        logger.debug("Token 已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"无效 Token: {e}")
        return None


def generate_admin_token() -> str:
    """生成管理员 Token（使用 Bot 管理员身份）

    Returns:
        str: JWT Token 字符串
    """
    return generate_token("admin")

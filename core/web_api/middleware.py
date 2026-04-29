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
认证中间件

拦截所有 /api 请求，验证 JWT Token，放行公开路径。
"""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from .auth import verify_token

logger = logging.getLogger(__name__)

# 不需要认证的路径
PUBLIC_PATHS = {
    "/api/auth/login",
    "/api/auth/telegram-callback",
    "/api/auth/status",
    "/api/health",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT 认证中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # 非 API 路径直接放行（静态文件等）
        if not path.startswith("/api"):
            return await call_next(request)

        # 公开路径放行
        if path in PUBLIC_PATHS:
            return await call_next(request)

        # OPTIONS 请求放行（CORS 预检）
        if request.method == "OPTIONS":
            return await call_next(request)

        # 提取 Token
        token = _extract_token(request)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "未提供认证 Token"},
            )

        # 验证 Token
        user = verify_token(token)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token 无效或已过期"},
            )

        # 将用户信息存入 request.state
        request.state.user = user

        return await call_next(request)


def _extract_token(request: Request) -> str | None:
    """从请求中提取 Token"""
    # 查询参数
    token = request.query_params.get("token")
    if token:
        return token

    # Authorization Header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None

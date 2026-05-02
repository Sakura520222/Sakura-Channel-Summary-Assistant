# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""测试 WebUI 访问日志中间件"""

import logging

import httpx
import pytest
from fastapi import FastAPI

from core.web_api.middleware import AccessLogMiddleware


@pytest.mark.unit
async def test_access_log_middleware_logs_request(caplog):
    """测试普通请求会记录精简访问日志"""
    app = FastAPI()
    app.add_middleware(AccessLogMiddleware)

    @app.get("/api/test")
    async def test_endpoint():
        return {"ok": True}

    with caplog.at_level(logging.INFO, logger="core.web_api.access"):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.get("/api/test")

    assert response.status_code == 200
    assert "WebUI 请求: GET /api/test status=200" in caplog.text


@pytest.mark.unit
async def test_access_log_middleware_logs_health_as_debug(caplog):
    """测试健康检查访问日志降为 DEBUG"""
    app = FastAPI()
    app.add_middleware(AccessLogMiddleware)

    @app.get("/api/health")
    async def health_endpoint():
        return {"status": "ok"}

    with caplog.at_level(logging.DEBUG, logger="core.web_api.access"):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.get("/api/health")

    assert response.status_code == 200
    assert "WebUI 请求: GET /api/health status=200" in caplog.text


@pytest.mark.unit
async def test_access_log_middleware_logs_exception(caplog):
    """测试异常请求会记录错误日志"""
    app = FastAPI()
    app.add_middleware(AccessLogMiddleware)

    @app.get("/api/error")
    async def error_endpoint():
        raise RuntimeError("boom")

    with caplog.at_level(logging.ERROR, logger="core.web_api.access"):
        with pytest.raises(RuntimeError):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app, raise_app_exceptions=True),
                base_url="http://testserver",
            ) as client:
                await client.get("/api/error")

    assert "WebUI 请求异常: GET /api/error" in caplog.text

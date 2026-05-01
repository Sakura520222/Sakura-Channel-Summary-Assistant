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
WebUI API 模块

提供 Web 管理界面的后端 API，基于 FastAPI 实现。
"""

__all__ = ["create_app"]


def _patch_starlette_router_compat() -> None:
    """兼容 FastAPI 与新版 Starlette Router 初始化参数差异。"""
    from starlette.routing import Router

    if getattr(Router.__init__, "_sakura_compat_patched", False):
        return

    original_init = Router.__init__

    def compatible_init(self, *args, **kwargs):
        kwargs.pop("on_startup", None)
        kwargs.pop("on_shutdown", None)
        return original_init(self, *args, **kwargs)

    compatible_init._sakura_compat_patched = True
    Router.__init__ = compatible_init


_patch_starlette_router_compat()


def create_app(*args, **kwargs):
    """懒加载 FastAPI 应用工厂，避免导入子模块时初始化完整路由树。"""
    from .app import create_app as _create_app

    return _create_app(*args, **kwargs)

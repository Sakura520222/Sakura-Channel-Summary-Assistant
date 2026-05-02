# Copyright 2026 Sakura-Bot
#
# 本项目采用 GNU Affero General Public License Version 3.0 (AGPL-3.0) 许可
#
# - 署名：必须提供本项目的原始来源链接
# - 相同方式共享：衍生作品必须采用相同的许可证
#
# 本项目源代码：https://github.com/Sakura520222/Sakura-Bot
# 许可证全文：参见 LICENSE 文件

"""测试统一日志配置模块"""

import logging
import tempfile
from pathlib import Path

import pytest

from core.infrastructure.logging import get_component_log_file_path, setup_component_logging


@pytest.mark.unit
def test_get_component_log_file_path_with_base_path():
    """测试根据主日志路径推导组件日志路径"""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_log_file = Path(temp_dir) / "logs" / "sakura-bot.log"

        result = get_component_log_file_path("qa-bot.log", str(base_log_file))

        assert result == str(base_log_file.parent / "qa-bot.log")


@pytest.mark.unit
def test_get_component_log_file_path_without_base_path():
    """测试使用默认日志目录推导组件日志路径"""
    result = get_component_log_file_path("webui.log")

    assert result == str(Path("logs") / "webui.log")


@pytest.mark.unit
def test_setup_component_logging_creates_file_handler():
    """测试组件日志会创建文件处理器且重复调用不重复添加"""
    with tempfile.TemporaryDirectory() as temp_dir:
        logger_name = "tests.component_logging"
        target_logger = logging.getLogger(logger_name)
        target_logger.handlers.clear()
        target_logger.propagate = True
        base_log_file = Path(temp_dir) / "logs" / "sakura-bot.log"

        first_path = setup_component_logging(
            component_name="Test",
            logger_names=[logger_name],
            log_level=logging.INFO,
            log_to_file=True,
            base_log_file_path=str(base_log_file),
            component_log_file_name="component.log",
            log_file_max_size=1024,
            log_file_backup_count=1,
            log_to_console=False,
        )
        second_path = setup_component_logging(
            component_name="Test",
            logger_names=[logger_name],
            log_level=logging.INFO,
            log_to_file=True,
            base_log_file_path=str(base_log_file),
            component_log_file_name="component.log",
            log_file_max_size=1024,
            log_file_backup_count=1,
            log_to_console=False,
        )

        assert first_path == second_path == str(base_log_file.parent / "component.log")
        assert len(target_logger.handlers) == 1
        assert isinstance(target_logger.handlers[0], logging.Handler)
        assert target_logger.propagate is False

        target_logger.info("组件日志测试")
        target_logger.handlers[0].flush()

        assert Path(first_path).exists()
        assert "组件日志测试" in Path(first_path).read_text(encoding="utf-8")

        target_logger.handlers.clear()
        target_logger.propagate = True

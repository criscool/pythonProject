# -*- coding: utf-8 -*-
"""
automation 新框架 - 全局 conftest.py

职责：
1. 在 pytest 启动时加载配置
2. 提供全局 fixtures
3. 配置日志系统
4. 为后续 auth/session fixtures 预留扩展点
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import pytest

from automation.core.config.loader import config as app_cfg
from automation.core.utils.path import get_automation_root, get_logs_dir, ensure_dir


# ==================== pytest 钩子 ====================


def pytest_addoption(parser):
    """添加自定义命令行参数"""
    parser.addoption(
        "--env",
        action="store",
        default=os.environ.get("AUTOMATION_ENV", "test"),
        help="指定运行环境: test, staging, prod (默认: test)",
    )


def pytest_configure(config):
    """pytest 启动时的配置钩子"""
    # 1. 加载框架配置
    env = config.getoption("--env", default="test")
    app_cfg.load(env=env)

    # 2. 配置日志
    log_dir = get_logs_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_dir / f"automation_{timestamp}.log"

    config.option.log_file = str(log_file)
    config.option.log_file_level = app_cfg.get("logging.file_level", "DEBUG")
    config.option.log_file_format = app_cfg.get(
        "logging.format", "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    config.option.log_file_date_format = "%Y-%m-%d %H:%M:%S"

    # 3. 配置 Allure（如果安装了 allure-pytest）
    allure_results = get_automation_root() / app_cfg.get(
        "allure.results_dir", "reports/allure-results"
    )
    ensure_dir(allure_results)
    if hasattr(config.option, "allure_report_dir"):
        config.option.allure_report_dir = str(allure_results)
        config.option.clean_alluredir = True

    # 4. 输出启动信息
    print(f"\n{'=' * 60}")
    print(f"  Automation Framework")
    print(f"  Environment: {app_cfg.env}")
    print(f"  Base URL:    {app_cfg.api.base_url}")
    print(f"  Log File:    {log_file}")
    print(f"{'=' * 60}\n")


def pytest_sessionfinish(session, exitstatus):
    """测试结束后清理"""
    # 清理旧日志，只保留最新 N 个
    max_files = app_cfg.get("logging.max_files", 7)
    log_dir = get_logs_dir()
    log_files = sorted(
        log_dir.glob("automation_*.log"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    for old_file in log_files[max_files:]:
        old_file.unlink(missing_ok=True)


# ==================== 全局 Fixtures ====================


@pytest.fixture(scope="session")
def app_config():
    """
    提供配置对象给测试用例

    使用方式:
        def test_example(app_config):
            base_url = app_config.api.base_url
    """
    return app_cfg


@pytest.fixture
def logger(request):
    """
    为每个测试提供独立的 logger

    使用方式:
        def test_example(logger):
            logger.info("测试开始")
    """
    test_name = request.node.name
    test_logger = logging.getLogger(f"automation.{test_name}")
    test_logger.setLevel(logging.DEBUG)

    if not test_logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f"[{test_name}] %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        test_logger.addHandler(handler)

    return test_logger


# ==================== 预留扩展点 ====================
# 后续阶段将在此添加：
# - @pytest.fixture(scope="session") def auth_token(): ...
# - @pytest.fixture(scope="session") def api_client(): ...
# - @pytest.fixture def db_session(): ...

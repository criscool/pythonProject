"""conftest.py - 极简版日志配置"""

import pytest
import logging
from datetime import datetime
from pathlib import Path

# ==================== 日志配置 ====================
PROJECT_ROOT = Path(__file__).parent.absolute()
log_dir = PROJECT_ROOT / "testLog"
log_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = log_dir / f"pytest_{timestamp}.log"


def cleanup_old_logs(keep=7):
    """只保留最新的 keep 个日志文件，删除多余的旧日志"""
    log_files = sorted(log_dir.glob("pytest_*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
    for old_file in log_files[keep:]:
        old_file.unlink()


# ==================== pytest 钩子 ====================

def pytest_configure(config):
    """配置pytest的日志系统"""
    config.option.log_file = str(log_file)
    config.option.log_file_level = "DEBUG"  # ✅ 字符串格式
    config.option.log_file_format = "%(asctime)s - %(levelname)s - %(message)s"
    config.option.log_file_date_format = "%Y-%m-%d %H:%M:%S"

    # 动态设置 allure 结果目录为项目根目录下的 testReport/allure-results
    allure_dir = str(PROJECT_ROOT / "testReport" / "allure-results")
    config.option.allure_report_dir = allure_dir
    config.option.clean_alluredir = True

    # 可选：打印日志文件路径
    print(f"\n日志文件: {log_file}")
    print(f"Allure结果目录: {allure_dir}\n")


def pytest_sessionfinish(session, exitstatus):
    """测试结束后，写入 Allure 环境信息 & 清理旧日志"""
    # 清理旧日志，只保留最新7个
    cleanup_old_logs(keep=7)

    import os
    allure_results_dir = os.path.join(str(PROJECT_ROOT), "testReport", "allure-results")
    if os.path.exists(allure_results_dir):
        env_file = os.path.join(allure_results_dir, "environment.properties")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"Python.Version=3.8.5\n")
            f.write(f"Platform=Windows 10\n")
            f.write(f"Project=pythonProject\n")
            f.write(f"Test.Framework=pytest\n")


# ==================== fixtures ====================

@pytest.fixture
def logger(request):
    """
    为每个测试提供 logger

    使用方式:
        def test_something(logger):
            logger.info("信息")
    """
    test_name = request.function.__name__
    test_logger = logging.getLogger(test_name)
    test_logger.setLevel(logging.DEBUG)

    if not test_logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f"[{test_name}] %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        test_logger.addHandler(handler)

    return test_logger
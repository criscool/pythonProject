# -*- coding: utf-8 -*-
"""
冒烟测试示例 - 验证新框架基础能力

本文件用于验证：
1. pytest 能识别并运行新框架下的测试
2. 配置加载正常
3. fixtures 注入正常
4. marker 标记生效
"""

import pytest


@pytest.mark.smoke
class TestFrameworkSmoke:
    """框架冒烟验证"""

    def test_config_loaded(self, app_config):
        """验证配置加载成功"""
        assert app_config is not None
        assert app_config.env in ("test", "staging", "prod")
        assert app_config.api.base_url is not None
        print(f"[PASS] 配置加载成功, env={app_config.env}, base_url={app_config.api.base_url}")

    def test_config_env_value(self, app_config):
        """验证环境配置值正确"""
        # 默认 test 环境下，base_url 应该是 test.yaml 中的值
        if app_config.env == "test":
            assert app_config.api.base_url == "https://172.16.8.190"
        print(f"[PASS] 环境配置值验证通过")

    def test_logger_available(self, logger):
        """验证 logger fixture 可用"""
        assert logger is not None
        logger.info("Logger fixture 注入成功")
        logger.debug("Debug 级别日志测试")
        print("[PASS] Logger fixture 正常工作")

    def test_config_nested_access(self, app_config):
        """验证配置支持嵌套访问"""
        # 点号路径访问
        timeout = app_config.get("api.timeout")
        assert timeout is not None
        assert isinstance(timeout, int)

        # 属性访问
        log_level = app_config.logging.level
        assert log_level is not None
        print(f"[PASS] 嵌套配置访问正常: timeout={timeout}, log_level={log_level}")

    def test_markers_registered(self):
        """验证自定义 markers 已注册（不会报 warning）"""
        # 如果 markers 未注册，--strict-markers 会报错
        # 这个测试本身被标记为 smoke，能运行到这里就说明 marker 注册成功
        print("[PASS] smoke marker 注册成功")

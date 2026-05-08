# -*- coding: utf-8 -*-
"""
配置模块

使用方式:
    from automation.core.config import config
    config.load(env="test")
    print(config.api.base_url)
"""

from automation.core.config.loader import config

__all__ = ["config"]

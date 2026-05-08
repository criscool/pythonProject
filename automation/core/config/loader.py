# -*- coding: utf-8 -*-
"""
配置加载引擎

职责：
1. 加载 settings.yaml 默认配置
2. 根据环境名加载 env/{env_name}.yaml 覆盖
3. 支持环境变量覆盖（AUTOMATION_ 前缀）
4. 提供全局单例访问点

加载优先级（后者覆盖前者）：
  settings.yaml < env/{name}.yaml < 环境变量

使用方式：
    from automation.core.config.loader import config
    print(config.get("api.base_url"))
    print(config.api.base_url)
"""

import os
import re
from pathlib import Path
from typing import Any, Optional

# 兼容多种 YAML 库：优先 PyYAML，回退 ruamel.yaml，最后用内置简易解析
_yaml_loader = None

try:
    import yaml
    _yaml_loader = "pyyaml"
except ImportError:
    try:
        from ruamel.yaml import YAML as _RuamelYAML
        _yaml_loader = "ruamel"
    except ImportError:
        _yaml_loader = "builtin"


def _parse_yaml_file(file_path: Path) -> dict:
    """
    解析 YAML 文件，自动选择可用的解析后端
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if _yaml_loader == "pyyaml":
        import yaml
        data = yaml.safe_load(content)
    elif _yaml_loader == "ruamel":
        from ruamel.yaml import YAML as _RuamelYAML
        from io import StringIO
        ry = _RuamelYAML()
        data = ry.load(StringIO(content))
    else:
        # 内置简易 YAML 解析（仅支持本项目所需的简单结构）
        data = _simple_yaml_parse(content)

    return data if isinstance(data, dict) else {}


def _simple_yaml_parse(content: str) -> dict:
    """
    极简 YAML 解析器 - 仅支持:
    - 键值对 (key: value)
    - 嵌套字典 (缩进表示层级)
    - 字符串/数字/布尔值
    - 列表 (- item)
    - 注释 (# ...)
    - 带引号的字符串

    不支持: 多行字符串、锚点、复杂引用等
    """
    result = {}
    stack = [(result, -1)]  # (当前字典, 缩进级别)

    for line in content.split("\n"):
        # 跳过空行和注释
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 计算缩进
        indent = len(line) - len(line.lstrip())

        # 回退到正确的层级
        while len(stack) > 1 and indent <= stack[-1][1]:
            stack.pop()

        current_dict = stack[-1][0]

        # 列表项: - value
        if stripped.startswith("- "):
            # 找到父级 key 对应的列表
            value = _parse_value(stripped[2:].strip())
            # 向上找到拥有此列表的 key
            parent = stack[-1][0]
            if isinstance(parent, dict):
                # 找最后一个 key
                last_key = list(parent.keys())[-1] if parent else None
                if last_key and isinstance(parent[last_key], list):
                    parent[last_key].append(value)
                elif last_key and parent[last_key] is None:
                    parent[last_key] = [value]
            elif isinstance(parent, list):
                parent.append(value)
            continue

        # 键值对: key: value
        match = re.match(r'^([^:]+?):\s*(.*)', stripped)
        if match:
            key = match.group(1).strip()
            value_str = match.group(2).strip()

            if value_str == "" or value_str.startswith("#"):
                # 下一级是嵌套字典或空值
                current_dict[key] = {}
                stack.append((current_dict[key], indent))
            elif value_str == "[]":
                current_dict[key] = []
            else:
                current_dict[key] = _parse_value(value_str)

    return result


def _parse_value(value_str: str) -> Any:
    """解析 YAML 值为 Python 类型"""
    # 去掉行尾注释
    if "  #" in value_str:
        value_str = value_str[:value_str.index("  #")].strip()

    # 带引号的字符串
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    # 布尔值
    if value_str.lower() in ("true", "yes", "on"):
        return True
    if value_str.lower() in ("false", "no", "off"):
        return False

    # None
    if value_str.lower() in ("null", "~", ""):
        return None

    # 数字
    try:
        if "." in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        pass

    # 普通字符串
    return value_str


class Config:
    """配置管理器 - 支持嵌套字典点号访问"""

    def __init__(self):
        self._data: dict = {}
        self._loaded = False

    def load(self, env: Optional[str] = None) -> "Config":
        """
        加载配置

        :param env: 环境名 (test/staging/prod)，如果为 None 则从以下来源获取：
                    1. 环境变量 AUTOMATION_ENV
                    2. settings.yaml 中的 env 字段
        """
        config_dir = Path(__file__).parent

        # Step 1: 加载默认配置
        settings_file = config_dir / "settings.yaml"
        if settings_file.exists():
            self._data = _parse_yaml_file(settings_file)

        # Step 2: 确定环境名
        if env is None:
            env = os.environ.get("AUTOMATION_ENV", self._data.get("env", "test"))
        self._data["env"] = env

        # Step 3: 加载环境配置并深度合并
        env_file = config_dir / "env" / f"{env}.yaml"
        if env_file.exists():
            env_data = _parse_yaml_file(env_file)
            self._data = self._deep_merge(self._data, env_data)

        # Step 4: 应用环境变量覆盖 (AUTOMATION_ 前缀)
        self._apply_env_overrides()

        self._loaded = True
        return self

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        通过点号路径获取配置值

        :param key_path: 如 "api.base_url", "logging.level"
        :param default: 默认值
        :return: 配置值
        """
        keys = key_path.split(".")
        value = self._data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any) -> None:
        """运行时动态设置配置（不持久化）"""
        keys = key_path.split(".")
        data = self._data
        for key in keys[:-1]:
            if key not in data or not isinstance(data[key], dict):
                data[key] = {}
            data = data[key]
        data[keys[-1]] = value

    @property
    def env(self) -> str:
        return self._data.get("env", "test")

    @property
    def api(self) -> "ConfigSection":
        return ConfigSection(self._data.get("api", {}))

    @property
    def auth(self) -> "ConfigSection":
        return ConfigSection(self._data.get("auth", {}))

    @property
    def headers(self) -> "ConfigSection":
        return ConfigSection(self._data.get("headers", {}))

    @property
    def allure(self) -> "ConfigSection":
        return ConfigSection(self._data.get("allure", {}))

    @property
    def logging(self) -> "ConfigSection":
        return ConfigSection(self._data.get("logging", {}))

    @property
    def test_data(self) -> "ConfigSection":
        return ConfigSection(self._data.get("test_data", {}))

    @property
    def runner(self) -> "ConfigSection":
        return ConfigSection(self._data.get("runner", {}))

    def to_dict(self) -> dict:
        """返回完整配置字典（调试用）"""
        return self._data.copy()

    # ==================== 私有方法 ====================

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """深度合并两个字典，override 覆盖 base"""
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = Config._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_env_overrides(self) -> None:
        """
        从环境变量注入覆盖配置
        格式: AUTOMATION_API_BASE_URL -> api.base_url
        """
        prefix = "AUTOMATION_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # AUTOMATION_API_BASE_URL -> api.base_url
                config_path = key[len(prefix):].lower().replace("__", ".")
                # 单下划线转为同级 key 的分隔
                # 双下划线转为层级分隔
                # 简化处理：仅支持双下划线作层级分隔
                parts = key[len(prefix):].lower().split("__")
                config_path = ".".join(parts)
                self.set(config_path, value)

    def __repr__(self) -> str:
        return f"<Config env={self.env} loaded={self._loaded}>"


class ConfigSection:
    """配置子节点，支持属性访问"""

    def __init__(self, data: dict):
        self._data = data

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)
        value = self._data.get(name)
        if isinstance(value, dict):
            return ConfigSection(value)
        return value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_dict(self) -> dict:
        return self._data.copy()

    def __repr__(self) -> str:
        return f"<ConfigSection {self._data}>"


# ==================== 全局单例 ====================
# 首次 import 时不自动加载，由 conftest.py 或 main.py 显式触发
config = Config()

"""
跨环境路径探测工具

自动查找 Java、Allure 等依赖工具的安装路径。
优先读取环境变量，其次扫描系统默认安装目录。
"""

import os
import platform
import shutil
from pathlib import Path
from typing import Callable, Optional


__all__ = [
    "PathDetector",
    "PathDetectionError",
]


class PathDetectionError(RuntimeError):
    """路径探测失败时抛出的异常"""


class PathDetector:
    """
    跨环境路径探测工具

    用法:
        detector = PathDetector()
        java_home = detector.find_java_home()      # -> Path
        allure_exe = detector.find_allure_path()    # -> Path
    """

    def __init__(self):
        self._java_cache: Optional[Path] = None
        self._allure_cache: Optional[Path] = None

    def reset_cache(self):
        """清空缓存，下次调用会重新探测"""
        self._java_cache = None
        self._allure_cache = None

    # ==================== 公共 API ====================

    def find_java_home(self) -> Path:
        """
        查找 Java 根目录 (JAVA_HOME)，优先级：
        1. JAVA_HOME 环境变量
        2. PATH 中的 java 可执行文件
        3. 系统默认安装目录
        """
        if self._java_cache is not None:
            return self._java_cache

        path = (
            self._from_env("JAVA_HOME", _is_java_home)
            or self._from_path("java", _resolve_java_home_from_exe)
            or self._scan_default_dirs(_get_java_candidates(), _is_java_home)
        )
        if path is None:
            raise PathDetectionError(
                "未找到 Java 安装目录。请设置 JAVA_HOME 环境变量或安装 JDK/JRE。"
            )
        self._java_cache = path
        return path

    def find_allure_path(self) -> Path:
        """
        查找 Allure 命令路径，优先级：
        1. ALLURE_HOME 环境变量
        2. PATH 中的 allure 可执行文件
        3. 系统默认安装目录
        """
        if self._allure_cache is not None:
            return self._allure_cache

        path = (
            self._from_env("ALLURE_HOME", _is_allure_home)
            or self._from_path("allure", _identity)
            or self._scan_default_dirs(_get_allure_candidates(), _is_allure_home)
        )
        if path is None:
            raise PathDetectionError(
                "未找到 Allure 命令。请安装 Allure 或将其所在目录加入 PATH。\n"
                "  下载: https://github.com/allure-framework/allure2/releases"
            )
        self._allure_cache = path
        return path

    # ==================== 底层策略 ====================

    @staticmethod
    def _from_env(var: str, validator: Callable) -> Optional[Path]:
        raw = os.environ.get(var)
        if not raw:
            return None
        path = Path(raw)
        if not path.exists():
            return None
        if validator(path):
            return path
        for child in sorted(path.iterdir()):
            if child.is_dir() and validator(child):
                return child
        return None

    @staticmethod
    def _from_path(name: str, resolver: Callable) -> Optional[Path]:
        exe_path = shutil.which(name)
        if not exe_path:
            return None
        return resolver(Path(exe_path).resolve())

    @staticmethod
    def _scan_default_dirs(
        candidates: list[Path], validator: Callable
    ) -> Optional[Path]:
        for candidate in candidates:
            if not candidate.exists():
                continue
            if candidate.is_dir() and validator(candidate):
                return candidate
            for child in sorted(candidate.iterdir()):
                if child.is_dir() and validator(child):
                    return child
        return None


# ==================== 校验器 & 解析器 ====================


def _is_java_home(dir_path: Path) -> bool:
    return (dir_path / "bin" / _exe("java")).is_file()


def _is_allure_home(dir_path: Path) -> bool:
    return (dir_path / "bin" / _exe("allure")).is_file()


def _resolve_java_home_from_exe(exe_path: Path) -> Optional[Path]:
    """从 java 可执行文件反推 JAVA_HOME（java.exe -> bin/ -> JAVA_HOME）"""
    parent = exe_path.parent.parent
    return parent if (parent / "bin" / _exe("java")).is_file() else None


def _identity(path: Path) -> Path:
    return path


# ==================== 候选目录 ====================


def _get_java_candidates() -> list[Path]:
    system = platform.system()
    if system == "Windows":
        pf = os.environ.get("ProgramFiles", "C:\\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        up = os.environ.get("USERPROFILE", "C:\\Users\\Default")
        return [
            Path(pf) / "Java",
            Path(pf86) / "Java",
            Path(pf) / "Eclipse Adoptium",
            Path(up) / ".jdks",
            Path(up) / "scoop" / "apps" / "java",
            Path(up) / "AppData" / "Local" / "JetBrains" / "Toolbox" / "apps",
            Path("C:\\tools"),
        ]
    if system == "Linux":
        return [
            Path("/usr/lib/jvm"),
            Path("/usr/local"),
            Path("/opt"),
            Path("/opt/java"),
        ]
    if system == "Darwin":
        return [
            Path("/Library/Java/JavaVirtualMachines"),
            Path("/usr/local"),
            Path("/opt/homebrew"),
        ]
    return []


def _get_allure_candidates() -> list[Path]:
    system = platform.system()
    if system == "Windows":
        pf = os.environ.get("ProgramFiles", "C:\\Program Files")
        up = os.environ.get("USERPROFILE", "C:\\Users\\Default")
        choco = os.environ.get("ChocolateyInstall", "C:\\ProgramData\\chocolatey")
        return [
            Path(pf) / "allure",
            Path(up) / "scoop" / "apps" / "allure" / "current",
            Path(choco) / "lib" / "allure",
            Path(up) / "AppData" / "Local" / "Programs" / "allure",
            Path("C:\\tools"),
        ]
    if system == "Linux":
        return [
            Path("/usr/local/share/allure"),
            Path("/opt/allure"),
            Path("/snap/allure"),
            Path("/usr/local"),
        ]
    if system == "Darwin":
        return [
            Path("/usr/local/share/allure"),
            Path("/opt/homebrew/opt/allure"),
            Path("/usr/local"),
        ]
    return []


# ==================== 平台工具函数 ====================


def _exe(name: str) -> str:
    """Windows 下追加 .exe"""
    return f"{name}.exe" if platform.system() == "Windows" else name

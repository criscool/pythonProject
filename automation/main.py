#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
automation 新框架 - 统一调度入口

职责：
1. 解析命令行参数（环境、运行范围、标记等）
2. 调度 pytest 执行测试
3. 为后续 CI/scripts 扩展预留空间

使用方式：
    # 运行全部测试（默认 test 环境）
    python main.py

    # 指定环境
    python main.py --env staging

    # 只运行冒烟测试
    python main.py --scope smoke

    # 只运行某个模块
    python main.py --scope tests/api

    # 只运行某个文件
    python main.py --scope tests/smoke/test_smoke_example.py

    # 运行指定标记的用例
    python main.py --mark smoke

    # 组合使用
    python main.py --env staging --mark regression --workers 4
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# 确保 automation 的父目录在 sys.path 中
AUTOMATION_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = AUTOMATION_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Automation Test Runner - 统一测试调度入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                          # 运行全部测试
  python main.py --env staging            # 指定环境
  python main.py --scope smoke            # 冒烟测试
  python main.py --scope tests/api        # API 模块测试
  python main.py --mark permission        # 按标记过滤
  python main.py --scope smoke --env test # 组合
        """,
    )

    parser.add_argument(
        "--env",
        default=os.environ.get("AUTOMATION_ENV", "test"),
        choices=["test", "staging", "prod"],
        help="运行环境 (default: test)",
    )

    parser.add_argument(
        "--scope",
        default="tests",
        help="运行范围: tests, tests/api, tests/smoke, 或具体文件路径 (default: tests)",
    )

    parser.add_argument(
        "--mark", "-m", default=None, help="pytest marker 过滤，如: smoke, regression, permission"
    )

    parser.add_argument(
        "--workers", "-w", type=int, default=1, help="并行 worker 数 (需安装 pytest-xdist)"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", default=True, help="详细输出 (default: True)"
    )

    parser.add_argument(
        "--report",
        action="store_true",
        default=False,
        help="测试结束后生成 Allure 报告",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="只显示将要执行的命令，不实际运行",
    )

    return parser.parse_args()


def build_pytest_args(args) -> list:
    """根据参数构建 pytest 命令行参数列表"""
    pytest_args = []

    # 运行范围
    pytest_args.append(args.scope)

    # 环境参数
    pytest_args.extend(["--env", args.env])

    # 详细模式
    if args.verbose:
        pytest_args.extend(["-v", "-s"])

    # 标记过滤
    if args.mark:
        pytest_args.extend(["-m", args.mark])

    # 并行
    if args.workers > 1:
        pytest_args.extend(["-n", str(args.workers)])

    # 短 traceback
    pytest_args.extend(["--tb", "short"])

    return pytest_args


def run(args) -> int:
    """执行测试"""
    import pytest

    pytest_args = build_pytest_args(args)

    print("=" * 60)
    print("  Automation Test Runner")
    print(f"  Environment : {args.env}")
    print(f"  Scope       : {args.scope}")
    print(f"  Markers     : {args.mark or 'all'}")
    print(f"  Workers     : {args.workers}")
    print(f"  Pytest Args : {' '.join(pytest_args)}")
    print("=" * 60)

    if args.dry_run:
        print(f"\n[DRY-RUN] pytest {' '.join(pytest_args)}")
        return 0

    # 切换工作目录到 automation/
    os.chdir(str(AUTOMATION_ROOT))

    exit_code = pytest.main(pytest_args)

    print(f"\n{'=' * 60}")
    print(f"  Tests finished with exit code: {exit_code}")
    print(f"{'=' * 60}")

    return exit_code


def generate_allure_report():
    """生成 Allure HTML 报告"""
    try:
        from automation.core.config.loader import config as app_cfg
        from automation.core.utils.path import get_automation_root, ensure_dir
        from automation.core.utils.detector import PathDetector, PathDetectionError
    except ImportError:
        print("[WARN] 无法加载 config，跳过报告生成")
        return False

    detector = PathDetector()

    try:
        allure_home = detector.find_allure_path()
        allure_cmd = str(allure_home)
    except PathDetectionError as e:
        print(f"[FAIL] {e}")
        return False

    try:
        java_home = detector.find_java_home()
        os.environ["JAVA_HOME"] = str(java_home)
    except PathDetectionError:
        pass

    automation_root = get_automation_root()
    results_dir = str(automation_root / app_cfg.get("allure.results_dir", "reports/allure-results"))
    report_dir = str(automation_root / app_cfg.get("allure.report_dir", "reports/allure-report"))

    ensure_dir(Path(report_dir).parent)

    print("\n" + "=" * 60)
    print("[REPORT] 生成 Allure 报告...")
    print("=" * 60)

    cmd = [allure_cmd, "generate", results_dir, "-o", report_dir, "--clean"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] 报告已生成: {report_dir}")
            _set_report_language(report_dir)
            return True
        else:
            print(f"[FAIL] 生成报告失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print(f"[FAIL] 找不到 Allure 命令: {allure_cmd}")
        return False


def _set_report_language(report_dir):
    """将 Allure 报告设置为中文"""
    index_html = os.path.join(report_dir, "index.html")
    if not os.path.exists(index_html):
        return

    with open(index_html, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace('lang="en"', 'lang="zh"')

    inject_script = """<script>
    Object.defineProperty(navigator, 'language', {get: function() {return 'zh-CN';}});
    Object.defineProperty(navigator, 'languages', {get: function() {return ['zh-CN', 'zh'];}});
    </script>
    <script src="app.js"></script>"""
    content = content.replace('<script src="app.js"></script>', inject_script)

    with open(index_html, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] 报告语言已设置为中文")


def main():
    """主入口"""
    args = parse_args()

    # 设置环境变量，确保 conftest.py 能获取到
    os.environ["AUTOMATION_ENV"] = args.env

    exit_code = run(args)

    # 可选：生成 Allure 报告
    if args.report:
        generate_allure_report()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

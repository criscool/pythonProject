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


def main():
    """主入口"""
    args = parse_args()

    # 设置环境变量，确保 conftest.py 能获取到
    os.environ["AUTOMATION_ENV"] = args.env

    exit_code = run(args)

    # 可选：生成 Allure 报告（后续阶段完善）
    if args.report:
        print("\n[INFO] Allure 报告生成功能将在后续阶段实现")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

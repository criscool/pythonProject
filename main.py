"""
main.py - 测试运行入口
功能：运行 pytest 测试 → 生成 Allure 报告
"""

import pytest
import subprocess
import os
import sys

from conf.base_configs import base_dir, allure_dir, java_home

# ==================== 配置 ====================
# Allure 命令行路径
ALLURE_CMD = allure_dir
# Java 环境（如果系统 JAVA_HOME 已配好可以删除这行）
os.environ["JAVA_HOME"] = java_home

# 项目根目录
PROJECT_ROOT = base_dir
# Allure 原始结果目录
ALLURE_RESULTS = os.path.join(PROJECT_ROOT, "testReport", "allure-results")
# Allure HTML 报告目录
ALLURE_REPORT = os.path.join(PROJECT_ROOT, "testReport", "allure-report")


def run_tests():
    """运行 pytest 测试"""
    print("=" * 60)
    print("[START] 开始运行测试...")
    print("=" * 60)

    # 注意：--alluredir 和 --clean-alluredir 已在 pytest.ini 中配置，这里不要重复传
    exit_code = pytest.main([
        "testCase/",
        "-v", "-s"
    ])

    print(f"\n[DONE] 测试运行完成，退出码: {exit_code}")
    return exit_code


def generate_report():
    """生成 Allure HTML 报告"""
    print("\n" + "=" * 60)
    print("[REPORT] 生成 Allure 报告...")
    print("=" * 60)

    cmd = [
        ALLURE_CMD,
        "generate",
        ALLURE_RESULTS,
        "-o", ALLURE_REPORT,
        "--clean"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] 报告已生成: {ALLURE_REPORT}")
            # 设置报告语言为中文
            set_report_language()
        else:
            print(f"[FAIL] 生成报告失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print(f"[FAIL] 找不到 Allure 命令: {ALLURE_CMD}")
        print("请确认 Allure 已安装并设置了正确路径")
        return False

    return True


def set_report_language():
    """将 Allure 报告设置为中文"""
    index_html = os.path.join(ALLURE_REPORT, "index.html")
    if not os.path.exists(index_html):
        return

    with open(index_html, "r", encoding="utf-8") as f:
        content = f.read()

    # 修改 html 标签的 lang 属性为 zh
    content = content.replace('lang="en"', 'lang="zh"')

    # 在 app.js 加载之前注入脚本，强制覆盖 navigator.language 为中文
    inject_script = """<script>
    Object.defineProperty(navigator, 'language', {get: function() {return 'zh-CN';}});
    Object.defineProperty(navigator, 'languages', {get: function() {return ['zh-CN', 'zh'];}});
    </script>
    <script src="app.js"></script>"""
    content = content.replace('<script src="app.js"></script>', inject_script)

    with open(index_html, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] 报告语言已设置为中文")

"""
#打开 Allure 报告（启动本地 HTTP 服务器查看已生成的报告）0-暂不需开启
def open_report():
    
    print("\n" + "=" * 60)
    print("[OPEN] 打开 Allure 报告...")
    print("=" * 60)

    cmd = [
        ALLURE_CMD,
        "open",
        ALLURE_REPORT
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n报告服务已关闭")
    except FileNotFoundError:
        print(f"[FAIL] 找不到 Allure 命令: {ALLURE_CMD}")
"""

if __name__ == "__main__":
    # 第1步：运行测试
    exit_code = run_tests()

    # 第2步：生成静态报告
    generate_report()

    # 第3步：打开报告（启动本地 HTTP 服务器自动在浏览器中查看）
    #open_report()


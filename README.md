# 🧪 API 自动化测试框架

基于 **pytest + Allure + Excel数据驱动** 的接口自动化测试框架。

---

## 📁 项目结构

```
pythonProject/
├── main.py                    # 🚀 入口文件：运行测试 → 生成报告 → 打开浏览器
├── conftest.py                # pytest 全局配置（日志、Allure、fixtures）
├── pytest.ini                 # pytest 配置文件
├── requirements.txt           # Python 依赖包
│
├── conf/                      # ⚙️ 配置目录
│   ├── base_configs.py        #   项目路径、Allure路径、Java环境
│   └── url_configs.py         #   接口地址、请求头、授权信息
│
├── lib/                       # 📚 工具库
│   ├── my_requests.py         #   HTTP 请求封装（支持 GET/POST/PUT/DELETE）
│   ├── excel_reader.py        #   Excel 读取工具类（openpyxl）
│   ├── test_Data.py           #   测试数据管理（缓存 + 多Sheet支持）
│   └── generrate_authorization.py  #   授权信息生成
│
├── testCase/                  # 🧪 测试用例目录
│   ├── events/
│   │   └── test_events.py     #   告警模块测试用例
│   └── asserts/
│       └── test_asserts.py    #   资产模块测试用例
│
├── testData/                  # 📊 测试数据（Excel）
│   └── APIInfo.xlsx           #   接口测试数据（多Sheet对应不同模块）
│
├── testLog/                   # 📝 测试日志（自动保留最新7个）
│
└── testReport/                # 📈 测试报告
    ├── allure-results/        #   Allure 原始结果数据
    └── allure-report/         #   Allure HTML 报告
```

---

## 🛠️ 环境准备

### 1. Python 环境

- **Python 3.8+**

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 Allure 命令行工具

1. 从 [Allure Releases](https://github.com/allure-framework/allure2/releases) 下载最新版本
2. 解压到本地目录（如 `D:\allure-2.38.1\`）
3. 在 `conf/base_configs.py` 中配置 Allure 路径：
   ```python
   allure_dir = r"D:\allure-2.38.1\bin\allure.bat"
   ```

### 4. Java 环境

Allure 依赖 Java 运行环境：
- 安装 **JDK 1.8+**
- 在 `conf/base_configs.py` 中配置（或设置系统环境变量 `JAVA_HOME`）：
  ```python
  java_home = r"C:\Program Files\Java\jdk1.8.0_152"
  ```

---

## 🚀 运行测试

### 方式一：通过 main.py 运行（推荐）

```bash
python main.py
```

执行流程：
1. ✅ 运行 pytest 测试用例
2. ✅ 生成 Allure HTML 报告
3. ✅ 自动设置报告语言为中文

> 如需自动打开浏览器查看报告，取消 `main.py` 中 `open_report()` 的注释即可。

### 方式二：直接运行 pytest

```bash
pytest testCase/ -v -s
```

然后手动生成报告：

```bash
allure generate testReport/allure-results -o testReport/allure-report --clean
allure open testReport/allure-report
```

---

## 📊 测试数据说明

测试数据存放在 `testData/` 目录下的 Excel 文件中。

### Excel 格式要求

| 字段名 | 说明 | 示例 |
|--------|------|------|
| test_num | 用例编号 | Case_001 |
| test_name | 用例名称 | 告警列表 |
| test_method | 请求方法 | POST |
| test_api | 接口路径 | /api/xxx |
| params | 请求参数（JSON字符串） | {"key": "value"} |
| response | 期望响应关键字 | data |

---

## ⚙️ 配置说明

### conf/url_configs.py

```python
# 接口基础地址
base_url = 'https://172.16.8.7'

# 请求头（不同环境需修改 authorization）
base_headers = {
    "Content-Type": "application/json",
    "authorization": "Basic xxxxxxxx"
}
```

### conf/base_configs.py

```python
# 项目根目录（自动获取）
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Allure 命令行路径
allure_dir = r"D:\allure-2.38.1\bin\allure.bat"

# Java 环境
java_home = r"C:\Program Files\Java\jdk1.8.0_152"
```

---

## 📝 日志管理

- 每次运行自动在 `testLog/` 目录生成带时间戳的日志文件
- 日志格式：`pytest_YYYY-MM-DD_HH-MM-SS.log`
- **自动清理**：只保留最新 7 个日志文件，旧的自动删除

---

## 📈 Allure 报告

报告生成后位于 `testReport/allure-report/` 目录，查看方式：

```bash
allure open testReport/allure-report
```

报告特性：
- 🌐 自动设置为中文界面
- 📊 包含环境信息（Python版本、平台、框架等）
- 📋 支持用例步骤展示、请求参数和响应结果附件

---

## 🔧 常见问题

### Q: 报告没有更新？
确保 `pytest.ini` 中包含 `--alluredir=testReport/allure-results --clean-alluredir`，并且 `conf/base_configs.py` 中 `base_dir` 路径正确。

### Q: 接口返回非200但用例显示通过？
检查测试用例的断言逻辑，确保对 `status_code` 做了 assert 断言，而不仅仅是 `logger.info()`。

### Q: Allure 命令找不到？
确认 `conf/base_configs.py` 中的 `allure_dir` 路径正确，并且已安装 Java 环境。

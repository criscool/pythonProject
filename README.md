<<<<<<< HEAD
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
=======
# pythonProject



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin http://172.16.8.220/yangxiutao/pythonproject.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](http://172.16.8.220/yangxiutao/pythonproject/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
>>>>>>> 05097dcbd75978bb9c1c0d184ad29d63d492b5e3

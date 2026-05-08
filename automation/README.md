# Automation Framework

> 新一代自动化测试框架，与旧框架并行存在，支持 API + UI 测试。

## 目录结构

```
automation/
├── core/                    # 核心基础设施
│   ├── config/              # 配置加载（YAML + 环境变量）
│   │   ├── loader.py        # 配置引擎
│   │   ├── settings.yaml    # 全局默认配置
│   │   └── env/             # 环境配置
│   │       ├── test.yaml
│   │       └── staging.yaml
│   ├── auth/                # 认证模块（后续实现）
│   ├── data/                # 数据管理
│   │   ├── loaders/         # 数据加载器
│   │   ├── providers/       # 数据提供者
│   │   └── factories/       # 数据工厂
│   ├── assertions/          # 自定义断言
│   ├── fixtures/            # 公共 fixtures
│   └── utils/               # 工具函数
├── api/                     # API 测试层
│   ├── client/              # HTTP 客户端封装
│   ├── modules/             # 业务模块接口
│   └── models/              # 数据模型
├── ui/                      # UI 测试层（后续实现）
│   ├── pages/               # Page Objects
│   ├── components/          # 组件封装
│   └── flows/               # 业务流程
├── tests/                   # 测试用例
│   ├── api/                 # API 测试用例
│   ├── ui/                  # UI 测试用例
│   ├── smoke/               # 冒烟测试
│   ├── regression/          # 回归测试
│   └── permission/          # 权限测试
├── testdata/                # 测试数据文件
├── main.py                  # 统一调度入口
├── conftest.py              # 全局 pytest 配置
├── pytest.ini               # pytest 配置文件
└── requirements.txt         # 依赖声明
```

## 快速开始

### 安装依赖

```bash
pip install -r automation/requirements.txt
```

### 运行测试

```bash
# 方式1: 通过 main.py 入口
cd automation
python main.py                          # 运行全部测试
python main.py --env staging            # 指定环境
python main.py --scope smoke            # 冒烟测试
python main.py --scope tests/api        # API 模块
python main.py --mark regression        # 按标记过滤

# 方式2: 直接使用 pytest
cd automation
pytest                                  # 运行全部
pytest tests/smoke -m smoke             # 冒烟
pytest --env staging                    # 指定环境
```

## 配置体系

配置加载优先级（后者覆盖前者）：

1. `core/config/settings.yaml` — 全局默认
2. `core/config/env/{env}.yaml` — 环境配置
3. 环境变量 `AUTOMATION_*` — 运行时覆盖

### 环境变量示例

```bash
export AUTOMATION_ENV=staging
export AUTOMATION_API__BASE_URL=https://new-server.com
export AUTOMATION_AUTH__AUTHORIZATION=Basic xxxx
```

## 与旧框架的关系

- 新旧框架**并行存在**，互不影响
- 旧框架（项目根目录下的 testCase/、conf/、lib/）保持不动
- 后续阶段逐步将旧用例迁移到新框架
- 迁移完成后旧目录可安全删除

# 自动化测试框架改造与 UI 扩展开发计划

## 1. 项目背景

当前 `/Users/ninebot/Downloads/pythonProject` 已具备一套基础 API 自动化测试框架，能够完成基于 `pytest + requests + Allure + Excel` 的接口测试执行与报告输出，但整体更偏“开发自用脚本式框架”，存在以下问题：

- 配置与环境强耦合，存在硬编码的 `base_url`、`authorization`、`Allure` 路径和 `JAVA_HOME`
- 目录结构偏粗糙，`conf / lib / testCase / testData` 分工不够清晰
- 测试用例承担了过多实现细节，包含数据解析、请求发送、断言、上下文传参、Allure 附件等逻辑
- 测试数据目前主要依赖 Excel，和执行逻辑耦合较深
- 当前框架仅覆盖 API，尚不具备 UI 自动化能力
- 代码有些过耦合，需要抽象处理

结合后续测试目标，需要在保留已有可用能力的基础上，对当前项目进行优化重构，并新增 UI 自动化测试能力，形成一套可持续演进的自动化测试框架。

## 2. 建设目标

本次改造的总体目标如下：

- 在现有项目内完成自动化框架的平滑重构，而不是直接推倒重建
- 保留已有 API 自动化中的可复用能力
- 新增一套结构清晰的 `automation` 测试框架目录
- 建立统一的 `core / api / ui / tests` 分层结构
- 支持 `API + UI` 一体化自动化测试
- 支持多环境切换和基础权限测试分类
- 支持后续逐步迁移旧 API 用例，降低切换风险

## 3. 改造思路

本项目建议采用 `平滑重构` 方案，而不是在现有目录基础上继续堆功能。

![alt text](image.png)
基于两者的对比，选择playwright进行UI自动化实现

### 3.1 核心原则

1. 在现有项目中新增 `automation/` 目录，承载新框架
2. 旧 API 用例保留一段兼容期，不立即删除
3. 现有可复用工具逐步迁移到新结构中
4. 新增 Playwright UI 能力，与 API 共用底座能力
5. 优先完成 MVP，可运行、可汇报、可交付

### 3.2 目标目录结构

```text
pythonProject/
  automation/
    core/
      config/
      auth/
      data/
      assertions/
      fixtures/
      utils/
    api/
      client/
      modules/
      models/
    ui/
      pages/
      components/
      flows/
    tests/
      api/
      ui/
      smoke/
      regression/
      permission/
    testdata/
    pytest.ini
    main.py
    conftest.py
    requirements.txt
    README.md
```

## 4. 现有项目能力复用建议

### 4.1 建议保留并迁移的内容

- `lib/excel_reader.py`
  读取 Excel 的基础能力可以保留，迁移到新框架的 `core/data/loaders/`

- `lib/test_Data.py`
  缓存和多 Sheet 数据读取思路可以保留，但需要拆分为 `loader / provider / factory`

- `lib/context.py`
  用例间上下文传值能力可以保留，迁移到新框架公共层

- `lib/schema_validator.py`
  JSON 结构校验能力可以保留，迁移到断言层

### 4.2 建议重构或替换的内容

- `conf/url_configs.py`
  需改为多环境配置文件，不再硬编码 `base_url` 和 `authorization`

- `conf/base_configs.py`
  需移除强依赖 Windows 本地路径的配置方式

- `lib/my_requests.py`
  需重构为更清晰的 `BaseClient + 模块 API 封装`

- `main.py`
  不再作为核心运行入口，仅保留脚本辅助用途，执行方式统一回归 `pytest + 脚本`

- `testCase/` 下现有测试
  后续逐步迁移至 `automation/tests/`，按 API/UI/测试集分类重组

  
> 当前项目已有一套基础 API 自动化能力，但整体结构偏粗糙，不适合直接叠加 UI 自动化。建议采用平滑重构方案，在现有项目内新增一套 `automation` 新框架，逐步迁移已有 API 能力，并同步接入 Playwright UI 自动化。整体计划分 3 个阶段推进，每阶段 1 周，预计 3 周完成首版可交付 MVP。

## 5. 开发阶段计划

### 阶段一：API 框架重构与基础骨架搭建

**周期：第 1 周**

#### 目标

完成新框架骨架建设，并将现有 API 基础能力迁移到新结构中。

#### 主要工作

- 在项目内新增 `automation/` 目录
- 建立 `core / api / tests` 基础结构
- 建立新的 `pytest.ini`、`conftest.py`、`requirements.txt`
- 建立多环境配置机制
- 重构公共配置、认证、日志、断言能力
- 重构测试数据访问层，支持 `json / yaml / excel`
- 重构 API 请求层为 `BaseClient + 模块 API 封装`
- 迁移首批已有 API 用例到新框架

#### 本阶段输出

- 新版自动化框架骨架
- 可运行的 API 能力层
- 至少 1~2 个模块的 API 用例迁移完成
- 旧框架仍可临时保留运行

#### 验收标准

- API 用例能跑通且 Allure 报告生成


### 阶段二：UI 自动化能力接入与代表场景落地

**周期：第 2 周**

#### 目标

在新框架中新增 UI 自动化能力，并完成代表性业务场景验证。

#### 主要工作

- 引入 `Playwright`
- 建立 `ui/pages`、`ui/components`、`ui/flows` 结构
- 封装登录页、仪表盘页、资产页、告警页等基础页面对象
- 封装表格、筛选器、菜单等通用组件
- 建立登录流、资产流、告警流等基础业务流
- 编写首批 UI 冒烟用例
- 打通 API 与 UI 的公共配置和数据能力

#### 本阶段输出

- UI 自动化基础框架
- 首批代表性 UI 用例可执行
- API 与 UI 在一个框架内共存并共享底座

#### 验收标准

- UI 冒烟用例能稳定执行、Playwright page object 成型
  

### 阶段三：测试集治理、权限分类与交付落地

**周期：第 3 周**

#### 目标

形成可用于团队协作和持续执行的 MVP 可交付版本。

#### 主要工作

- 按 `smoke / regression / permission` 对测试集进行分组
- 增加基础权限测试能力
- 建立统一执行脚本
- 接入 Allure 报告输出
- 增加 CI 执行入口
- 完善框架使用文档和迁移说明
- 梳理旧用例迁移路径和后续下线方案

#### 本阶段输出

- 可交付的 MVP 自动化框架
- 可执行的冒烟、回归、权限测试集
- 本地执行与 CI 执行入口
- 可用于团队推广的使用文档

#### 验收标准

- 稳定执行，并输出报告。
- 用例新增和维护体系成型


## 6. 主要风险与控制措施

### 风险一：旧框架和新框架并存期间维护成本上升

**控制措施：**

- 明确兼容期范围
- 先迁移代表性模块
- 避免双边长期并行开发

### 风险二：UI 自动化接入后框架复杂度明显上升

**控制措施：**

- UI 部分严格采用 `pages / components / flows` 分层
- 测试层不直接写定位器和细节逻辑

### 风险三：测试数据管理继续与执行逻辑耦合

**控制措施：**

- 将数据访问统一下沉到 `core/data`
- 测试用例不直接读取 Excel

### 风险四：开发周期内功能范围扩张

**控制措施：**

- 先做 MVP
- 只覆盖代表性 API/UI 模块
- 实时事件、异步任务等能力后续扩展

## 7. 最终交付物

本次开发计划完成后，预期交付如下：

- 一套新的 `automation/` 自动化测试框架
- 支持 API 与 UI 共存的测试结构
- 可复用的公共配置、数据、断言、fixtures 能力
- 首批代表性 API 用例
- 首批代表性 UI 用例
- 可运行的 `smoke / regression / permission` 测试集
- Allure 报告能力
- 基础 CI 集成能力
- 框架使用说明与迁移说明

## 8. 结论

综合当前项目现状与后续扩展目标，建议本项目采用 `平滑重构 + UI 能力接入` 的方案推进，而不是在现有结构基础上继续叠加功能。

该方案的优势在于：

- 能最大化复用现有 API 能力
- 能降低一次性推翻重建的风险
- 能较自然地接入 UI 自动化
- 能在 3 周内形成一版可交付的 MVP

建议按本开发计划推进实施，并在第 1 周结束后进行一次阶段评审，确认 API 重构骨架与目录结构稳定，再继续进入 UI 和交付阶段。


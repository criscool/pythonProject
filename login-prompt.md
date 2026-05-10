# 提示词：登录鉴权链路实现

你是一名资深测开工程师兼 Python 自动化测试架构师，现在请基于一个已经完成基础骨架的新测试框架，专门实现“登录鉴权链路”。

## 一、当前背景

当前情况：
- 新框架基础骨架已经完成
- 已具备 `automation/` 目录结构
- 当前只需要实现“登录 -> 获取 sessionid -> 转换 authorization -> 后续接口自动复用”这一整套能力
- 不要做 UI
- 这轮只聚焦认证链路和 pytest 中的复用机制

## 二、已知条件

以下信息我已经掌握，不需要你再猜测或设计认证协议：

1. 登录请求地址：https://172.16.8.189/api/system/sessions
2. 登录请求参数：host:ip地址,username: 加密的用户名,password, 加密的密码
3. 登录加密方式：有两个地方需要加密，首先用户名和密码是通过 这个是通过AES加密 AES对称加密CBC模式 AES密钥和AES偏移量是1234567812345678 第二个地方就是根据拿到的sessionId拼接:session 然后通过base64编码 转成token
4. 如何从登录响应中获取 `sessionid`：请求上文的url在响应里session_id获得对应的值
5. 如何将 `sessionid` 转换成 `authorization`：在第3部获取token 前面添加Basic token 作为authorization的key 格式：Authorization: Basic token

你的任务不是再讨论方案，而是把这套已知逻辑落地进 pytest 自动化框架中。

## 三、本轮目标

请完成以下能力建设：

### 1. 登录能力封装
实现独立的登录 API 能力，包括：
- 用户名密码传入
- 按已知加密方式处理参数
- 调用登录接口
- 解析响应
- 提取 `sessionid`
- 转换出 `authorization`

### 2. 鉴权上下文管理
实现统一的鉴权管理机制，要求：
- 不允许每条业务接口都手工传 `authorization`
- 不允许继续手工修改旧配置文件中的 `authorization`
- 登录后拿到的 `authorization` 应自动进入统一上下文
- 后续接口请求可自动复用

### 3. pytest 级复用
在 pytest 中实现以下能力：
- 可通过 fixture 注入用户名、密码
- 可通过 fixture 自动完成登录
- 可通过 fixture 或 session 级上下文拿到 `authorization`
- 后续 API 用例可直接复用登录态

### 4. 首条验证用例
除了登录用例本身，还要增加至少 1 条“依赖登录态”的业务接口验证用例，用来证明：
- 登录成功
- authorization 注入成功
- 后续业务接口无需手工改请求头
- pytest 下整条链路可跑通

## 四、实现要求

### 1. 必须优先实现这些能力
建议优先文件包括但不限于：

- `automation/api/modules/login_api.py`
- `automation/core/auth/session.py`
- `automation/core/auth/login.py`
- `automation/api/client/base_client.py`
- `automation/core/fixtures/api_fixtures.py`
- `automation/tests/api/test_login_api.py`
- `automation/tests/api/test_xxx_api.py`

### 2. 认证逻辑必须下沉
不要把登录、sessionid 提取、authorization 转换逻辑直接写在测试用例里。

要求分层清晰：
- `login_api.py`：负责登录接口调用
- `session.py` 或类似模块：负责 sessionid / authorization 管理
- `fixture`：负责 pytest 复用
- `test_*.py`：只负责验证

### 3. BaseClient 必须支持自动鉴权
后续业务接口在调用时，应能自动带上登录后的 `authorization`。

也就是说，业务接口测试代码最终应该接近这种风格：

```python
def test_xxx(api_client):
    result = api_client.some_business_api(...)
    assert ...
```

而不是这样：

```python
def test_xxx():
    login()
    token = ...
    headers = {"authorization": token}
    requests.post(...)
```

### 4. 不要开始 UI 和批量迁移
本轮不要：
- 接入 Playwright
- 编写页面对象
- 大量迁移 asserts/events 全部用例

只做认证链路和最小业务验证闭环。

## 五、你需要输出的内容

请按下面顺序执行：

### 第一步：先分析实现点
先输出：
1. 认证链路准备怎么分层
2. 计划新增/修改哪些文件
3. 每个文件负责什么
4. pytest 里准备怎么复用登录态

### 第二步：开始实施
按顺序实现：
1. 登录接口封装
2. sessionid 提取
3. authorization 转换
4. 鉴权上下文管理
5. BaseClient 自动注入 authorization
6. pytest fixture 复用
7. 登录测试用例
8. 首条依赖鉴权的业务测试用例

### 第三步：完成后给出验证方式
必须明确说明：
1. 如何验证用户名密码登录成功
2. 如何验证 sessionid 提取成功
3. 如何验证 authorization 转换成功
4. 如何验证后续请求自动带鉴权
5. 如何验证 pytest 下可以复用登录态

## 六、验收标准

本轮完成后，必须达到以下结果：

1. 已实现统一登录 API 能力
2. 已实现 sessionid -> authorization 转换逻辑
3. 已实现 session 级或 fixture 级鉴权上下文
4. BaseClient 可自动注入 authorization
5. `test_login_api.py` 可独立执行通过
6. 至少 1 条依赖鉴权的业务接口测试可执行通过
7. 后续业务测试不再需要手工修改 `authorization`

## 七、注意事项

1. 既然登录地址、参数、加密方式、sessionid 处理规则都已经明确，就不要再重新设计认证方案。
2. 如果你发现实现中需要具体常量值、字段名、请求结构，请从项目现有配置或用户已提供信息中读取，不要臆造。
3. 保持改动聚焦，只围绕认证链路做建设。
4. 输出时优先给出具体文件级计划，再动手实现。

现在开始：
先输出“认证链路分层设计 + 文件修改计划 + pytest 复用方案”，然后再开始编码实现。
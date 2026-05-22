"""
登录 API 封装

职责：
1. 接收用户名、密码、主机地址
2. 使用 AES 加密用户名和密码
3. 调用 POST /api/system/sessions
4. 返回登录响应
"""


from automation.core.config.loader import config
from automation.core.auth.crypto import aes_encrypt
from automation.core.auth.session import AuthSession


def login(username: str = None, password: str = None, host: str = None) -> dict:
    """
    执行登录，返回完整响应 JSON

    参数可以从以下来源获取（优先级从高到低）：
    1. 显式传入
    2. AuthSession 中设置的 credentials
    3. config 中的默认值

    :param username: 登录用户名（明文）
    :param password: 登录密码（明文）
    :param host: 主机地址
    :return: 登录接口响应的 JSON
    """
    session = AuthSession()
    creds = session.get_credentials()

    import re

    final_username = username or creds.get("username") or config.get("auth.username", "superadmin")
    final_password = password or creds.get("password") or config.get("auth.password", "")
    final_host = host or creds.get("host") or config.get("api.base_url", "")

    # 提取纯 IP/域名（去掉协议前缀），用于请求 body 中的 host 字段
    host_match = re.match(r"https?://([^/]+)", final_host)
    host_ip = host_match.group(1) if host_match else final_host

    # 加密用户名和密码
    encrypted_username = aes_encrypt(final_username)
    encrypted_password = aes_encrypt(final_password)

    # 构建请求参数
    payload = {
        "host": host_ip,
        "username": encrypted_username,
        "password": encrypted_password,
    }

    # 发送登录请求
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    login_path = config.get("auth.login_path", "/api/system/sessions")
    login_url = f"{final_host}{login_path}"
    headers = {
        "Content-Type": "application/json",
        "X-Requested-By": "XMLHttpRequest",
    }

    resp = requests.post(login_url, json=payload, headers=headers, verify=False, timeout=30)
    resp.raise_for_status()
    resp_json = resp.json()
    # 登录成功自动提取 session_id 并生成 authorization
    if resp_json.get("code"):
        return resp_json
    session.login_from_response(resp_json)

    return resp_json

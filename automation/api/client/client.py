"""
封装HTTP请求客户端
从新架构 config 系统获取请求头和 base_url
"""

import requests
import urllib3

from automation.core.config.loader import config
from automation.core.auth.session import AuthSession


class ApiClient:
    def __init__(self, base_url=None, headers=None, verify_ssl=None):
        self.base_url = base_url or config.get("api.base_url", "")
        self.verify_ssl = verify_ssl if verify_ssl is not None else config.get("api.verify_ssl", False)

        if headers:
            self.headers = headers
        else:
            self.headers = {
                "Content-Type": config.get("headers.content_type", "application/json"),
                "X-Requested-By": config.get("headers.x_requested_by", "XMLHttpRequest"),
                "X-Requested-With": config.get("headers.x_requested_with", "XMLHttpRequest"),
            }
            # 优先使用配置中的静态 authorization
            auth_value = config.get("auth.authorization")
            if auth_value:
                self.headers["authorization"] = auth_value
            else:
                # 无静态配置时，自动读取动态登录态（由 login_fixture 填充）
                auth_session = AuthSession()
                if auth_session.is_logged_in:
                    self.headers["authorization"] = auth_session.authorization

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def send_request(self, method, url, json=None, headers=None, verify=None):
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        verify_ssl = verify if verify is not None else self.verify_ssl
        full_url = url if url.startswith("http") else self.base_url + url

        method = method.upper()
        if method == "GET":
            resp = requests.request(method, full_url, params=json, headers=request_headers, verify=verify_ssl)
        else:
            resp = requests.request(method, full_url, json=json, headers=request_headers, verify=verify_ssl)
        return resp

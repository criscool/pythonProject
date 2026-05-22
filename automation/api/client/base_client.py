"""
增强版 HTTP 客户端
- 自动从 AuthSession 注入 authorization
- 自动拼接 base_url
- 支持 GET/POST/PUT/DELETE 快捷方法
"""

import requests
import urllib3

from automation.core.config.loader import config
from automation.core.auth.session import AuthSession


class BaseClient:
    """
    统一 API 客户端，自动携带登录后的鉴权信息

    使用方式：
        client = BaseClient()
        resp = client.post("/api/some/endpoint", json={...})
    """

    def __init__(self, base_url=None, verify_ssl=None):
        self.base_url = (base_url or config.get("api.base_url", "")).rstrip("/")
        self.verify_ssl = verify_ssl if verify_ssl is not None else config.get("api.verify_ssl", False)
        self._session = requests.Session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _build_headers(self, headers: dict = None) -> dict:
        """构建请求头，自动注入 authorization"""
        request_headers = {
            "Content-Type": "application/json",
            "X-Requested-By": "XMLHttpRequest",
            "X-Requested-With": "XMLHttpRequest",
        }

        # 从 AuthSession 自动注入 authorization（如果已登录）
        auth_session = AuthSession()
        if auth_session.is_logged_in:
            request_headers["authorization"] = auth_session.authorization

        if headers:
            request_headers.update(headers)
        return request_headers

    def _build_url(self, url: str) -> str:
        """拼接完整 URL"""
        if url.startswith("http"):
            return url
        return f"{self.base_url}/{url.lstrip('/')}"

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """通用请求方法"""
        headers = self._build_headers(kwargs.pop("headers", None))
        full_url = self._build_url(url)
        verify = kwargs.pop("verify", self.verify_ssl)

        return self._session.request(
            method=method,
            url=full_url,
            headers=headers,
            verify=verify,
            **kwargs,
        )

    def get(self, url: str, params=None, **kwargs) -> requests.Response:
        return self.request("GET", url, params=params, **kwargs)

    def post(self, url: str, json=None, data=None, **kwargs) -> requests.Response:
        return self.request("POST", url, json=json, data=data, **kwargs)

    def put(self, url: str, json=None, **kwargs) -> requests.Response:
        return self.request("PUT", url, json=json, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        return self.request("DELETE", url, **kwargs)

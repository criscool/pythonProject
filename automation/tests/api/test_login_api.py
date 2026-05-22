"""
登录鉴权链路测试

验证：
1. AES 加密功能正常
2. session_id → authorization 转换正常
3. 登录接口可正常调用并提取 session_id
4. BaseClient 自动注入 authorization
"""

import base64
import pytest
import allure

from automation.core.auth.crypto import aes_encrypt
from automation.core.auth.session import AuthSession
from automation.api.modules.login_api import login
from automation.conftest import load_test_data


class TestCrypto:
    """AES 加密 + Base64 编解码测试"""

    def test_aes_encrypt_returns_string(self):
        result = aes_encrypt("test")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_aes_encrypt_different_inputs(self):
        r1 = aes_encrypt("hello")
        r2 = aes_encrypt("world")
        assert r1 != r2

    def test_aes_encrypt_is_base64(self):
        result = aes_encrypt("superadmin")
        # 验证是合法的 base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_aes_encrypt_same_input_produces_same_output(self):
        """固定 IV 的情况下，相同输入产生相同输出"""
        r1 = aes_encrypt("same_text")
        r2 = aes_encrypt("same_text")
        assert r1 == r2


class TestAuthSession:
    """鉴权会话管理测试"""

    def setup_method(self):
        AuthSession().clear()

    def test_convert_session_id(self):
        session_id = "763dd028-1665-4229-8ab8-dab501f9dc76"
        auth = AuthSession.convert_session_id_to_auth(session_id)
        expected_raw = f"{session_id}:session"
        expected_b64 = base64.b64encode(expected_raw.encode()).decode()
        assert auth == f"Basic {expected_b64}"

    def test_login_from_response(self):
        session = AuthSession()
        resp = {"session_id": "test-session-123", "other": "data"}
        auth = session.login_from_response(resp)
        assert session.session_id == "test-session-123"
        assert session.is_logged_in is True
        assert "Basic" in auth
        assert "test-session-123" in base64.b64decode(auth.replace("Basic ", "")).decode()

    def test_login_from_response_missing_session_id(self):
        session = AuthSession()
        with pytest.raises(ValueError, match="session_id"):
            session.login_from_response({"error": "no session"})

    def test_clear(self):
        session = AuthSession()
        session.authorization = "Basic xyz"
        session.session_id = "abc"
        session.clear()
        assert session.is_logged_in is False
        assert session.authorization is None

    def test_singleton(self):
        s1 = AuthSession()
        s2 = AuthSession()
        assert s1 is s2


class TestLoginFlow:
    """登录集成测试（依赖实际服务器）"""


    @pytest.mark.smoke
    def test_login_and_auth_chain(self, login_session):
        """端到端验证：登录 → 获取 session_id → authorization 可用"""
        session = login_session
        assert session.is_logged_in
        assert session.session_id is not None
        assert session.authorization is not None
        assert session.authorization.startswith("Basic ")

    @pytest.mark.smoke
    def test_base_client_auto_injects_auth(self, api_client):
        """验证 BaseClient 自动携带 authorization"""
        resp = api_client.post("/api/plugins/com.andisec.plugins.alarm/events/searchv2", json={
            "query": " status:0",
            "sort": [],
            "page": 1,
            "per_page": 20,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data
        assert "total" in data



@allure.severity(allure.severity_level.NORMAL)
@allure.epic("针对单个接口测试")
@allure.feature("用户登录模块")
class TestUserLogin():

    @pytest.mark.single
    @pytest.mark.parametrize("username,password,except_result,except_msg",
        load_test_data("test_login_user"))
    def test_login_user(self, username, password, except_result, except_msg, ):
        
        result = login(username, password)
        
        if except_result:
            assert result.get("session_id") is not None
            assert result.get("password_expired") is False
        else:
            assert "code" in result
            assert result["code"] == "ApiError"
            assert except_msg in result["msg"]



@allure.severity(allure.severity_level.CRITICAL)
@allure.epic("针对单个接口测试")
@allure.feature("用户登录模块-边界与异常")
class TestLoginEdgeCases:
    """等价类划分、边界值分析等扩展用例"""

    def _direct_login(self, username, password):
        """绕过 login() 的 or 回退逻辑，直接发送登录请求"""
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        from automation.core.auth.crypto import aes_encrypt
        from automation.core.config.loader import config

        payload = {
            "host": config.get("api.base_url", "").replace("https://", "").replace("http://", ""),
            "username": aes_encrypt(username),
            "password": aes_encrypt(password),
        }
        login_url = f'{config.get("api.base_url", "")}{config.get("auth.login_path", "/api/system/sessions")}'
        headers = {"Content-Type": "application/json", "X-Requested-By": "XMLHttpRequest"}
        resp = requests.post(login_url, json=payload, headers=headers, verify=False, timeout=30)
        return resp.json()

    def _is_error_response(self, result):
        """检查响应是否为错误（兼容两种错误格式）"""
        return "code" in result or "type" in result

    @pytest.mark.negative
    @allure.title("用户名为空字符串")
    def test_login_empty_username(self):
        """等价类：用户名为空"""
        result = self._direct_login("", "Admin@123")
        assert self._is_error_response(result), f"空用户名应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("密码为空字符串")
    def test_login_empty_password(self):
        """等价类：密码为空"""
        result = self._direct_login("superadmin", "")
        assert self._is_error_response(result), f"空密码应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("用户名和密码均为空")
    def test_login_empty_both(self):
        """等价类：用户名和密码同时为空"""
        result = self._direct_login("", "")
        assert self._is_error_response(result), f"用户名密码均为空应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("用户名为空白字符")
    def test_login_whitespace_username(self):
        """等价类：用户名仅为空格/制表符"""
        result = self._direct_login("   ", "Admin@123")
        assert self._is_error_response(result), f"空白用户名应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("密码为空白字符")
    def test_login_whitespace_password(self):
        """等价类：密码仅为空格/制表符"""
        result = self._direct_login("superadmin", "   ")
        assert self._is_error_response(result), f"空白密码应该返回错误，实际: {result}"

    @pytest.mark.smoke
    @allure.title("用户名和密码均正确-冒烟")
    def test_login_valid_credentials_direct(self):
        """冒烟：正向用例通过直接API验证"""
        result = self._direct_login("superadmin", "Admin@123")
        assert result.get("session_id") is not None, f"登录应该成功，实际: {result}"

    @pytest.mark.negative
    @allure.title("超长用户名（256字符）边界值")
    def test_login_very_long_username(self):
        """边界值：超长用户名"""
        long_name = "a" * 256
        result = self._direct_login(long_name, "Admin@123")
        assert "code" in result, f"超长用户名应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("超长密码（256字符）边界值")
    def test_login_very_long_password(self):
        """边界值：超长密码"""
        long_pwd = "b" * 256
        result = self._direct_login("superadmin", long_pwd)
        assert "code" in result, f"超长密码应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("用户名含SQL注入关键字")
    def test_login_sql_injection_username(self):
        """特殊值：SQL注入尝试"""
        result = self._direct_login("' OR 1=1 --", "Admin@123")
        assert "code" in result, f"SQL注入用户名应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("密码含SQL注入关键字")
    def test_login_sql_injection_password(self):
        """特殊值：密码SQL注入尝试"""
        result = self._direct_login("superadmin", "' OR '1'='1")
        assert "code" in result, f"SQL注入密码应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("用户名含特殊字符")
    def test_login_special_chars_username(self):
        """等价类：特殊字符用户名"""
        result = self._direct_login("admin@#$%^&*()", "Admin@123")
        assert "code" in result, f"特殊字符用户名应该返回错误，实际: {result}"

    @pytest.mark.negative
    @allure.title("Unicode用户名")
    def test_login_unicode_username(self):
        """等价类：Unicode用户名"""
        result = self._direct_login("管理员", "Admin@123")
        assert "code" in result, f"Unicode用户名应该返回错误，实际: {result}"


if __name__ == '__main__':
    pytest.main("-q", "-s", "test_login_api.py")


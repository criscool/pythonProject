"""
业务接口验证测试
依赖登录鉴权，验证 BaseClient 自动注入 authorization 后能正常调用业务接口
"""

import pytest


class TestEventApi:
    """告警模块业务接口测试 - 依赖登录态"""

    @pytest.mark.smoke
    def test_events_search(self, api_client):
        """告警列表查询 - 验证登录态复用"""
        resp = api_client.post("/api/plugins/com.andisec.plugins.alarm/events/searchv2", json={
            "query": " status:0",
            "sort": [],
            "page": 1,
            "per_page": 20,
        })
        assert resp.status_code == 200, f"请求失败: {resp.status_code}"
        body = resp.json()
        assert "events" in body, "响应缺少 events 字段"
        assert isinstance(body.get("events"), list)

    @pytest.mark.smoke
    def test_events_search_no_auth_needed_manually(self, api_client):
        """
        验证：业务测试不需要手动处理 authorization
        这个测试如果通过，说明 authorization 被自动注入
        """
        resp = api_client.post("/api/plugins/com.andisec.plugins.alarm/events/searchv2", json={
            "query": " status:0",
            "sort": [],
            "page": 1,
            "per_page": 20,
        })
        # 如果是 401 说明鉴权没自动注入
        assert resp.status_code != 401, "authorization 未自动注入，返回了 401"
        assert resp.status_code == 200

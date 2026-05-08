import json


import pytest

from conf.url_configs import base_url
from conftest import logger

from lib.my_requests import MyRequests
from lib.test_Data import TestData

import allure

# 导入 JSON 结构校验相关函数
from lib.schema_validator import compare_json_structure


# 从 Excel 读取所有测试数据
test_data = TestData.get_all("APIInfo.xlsx", "events")


@pytest.mark.parametrize(
    "case",
    test_data,
    ids=[f"Case_{d.get('test_num', i)}-{d.get('test_name', '')}"
         for i, d in enumerate(test_data)]
)
@allure.feature("告警模块")
def test_events(case, logger):
    # 动态设置 allure 标题为用例名称
    allure.dynamic.title(f"用例_{case.get('test_num', '')}-{case.get('test_name', '')}")

    logger.info("开始测试"+case.get('test_name')+"接口")
    logger.debug("准备测试数据...")

    with allure.step("步骤1：解析测试数据"):
        case_num = case.get('test_num')
        case_name = case.get('test_name')
        case_method = case.get('test_method')
        case_api = case['test_api']
        case_api_full = base_url + case_api
        case_params = case.get('params')
        reqParam = json.JSONDecoder().decode(case_params)
        case_response = case.get('response')
        allure.attach(str(reqParam), name="请求参数", attachment_type=allure.attachment_type.JSON)

    with allure.step("步骤2：发送API请求"):
        my_requests = MyRequests()
        res = my_requests.send_requests(
            method=case_method, url=case_api_full,
            json=reqParam, headers=None, verify=False
        )
        allure.attach(f"状态码: {res.status_code}\n响应: {res.text}",
                      name="响应结果", attachment_type=allure.attachment_type.TEXT)

    with allure.step("步骤3：验证响应结果"):
        assert res.status_code == 200, f"请求失败，期望状态码200，实际状态码: {res.status_code}，响应: {res.text}"
        res_json = res.json()

        # 判断 response 字段是 JSON 结构还是普通字符串
        is_json_schema = False
        if case_response and case_response.strip().startswith('{'):
            try:
                expected_json = json.loads(case_response)
                is_json_schema = True
            except json.JSONDecodeError:
                is_json_schema = False

        if is_json_schema:
            # ===== JSON 结构校验：直接对比 Excel 中的 JSON 和实际返回的 JSON 的 key 结构 =====
            is_pass, missing_keys, extra_keys = compare_json_structure(res_json, expected_json)

            allure.attach(
                json.dumps(expected_json, ensure_ascii=False, indent=2),
                name="期望JSON（来自Excel）",
                attachment_type=allure.attachment_type.JSON
            )

            if missing_keys:
                logger.warning(f"实际响应中缺少的字段: {sorted(missing_keys)}")
            if extra_keys:
                logger.info(f"实际响应中多出的字段（不影响通过）: {sorted(extra_keys)}")

            if not is_pass:
                error_msg = f"JSON结构校验失败，实际响应中缺少以下字段:\n" + "\n".join(sorted(missing_keys))
                allure.attach(error_msg, name="结构校验错误详情", attachment_type=allure.attachment_type.TEXT)
                assert False, error_msg
            else:
                logger.info("JSON结构断言通过 ✅")
                allure.attach("实际响应包含期望JSON的所有字段", name="结构校验结果", attachment_type=allure.attachment_type.TEXT)
        else:
            # ===== 原有逻辑：检查某个 key 是否存在 =====
            assert case_response in res_json, \
                f"断言失败，期望响应中包含: {case_response}，实际响应: {res_json}"

        logger.info("断言成功")

    logger.info("测试完成"+case.get('test_name')+"接口")



if __name__ == '__main__':
    pytest.main([__file__, "-v", "-s"])

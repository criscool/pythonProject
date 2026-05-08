import json
import re

import pytest

from conf.url_configs import base_url
from conftest import logger

from lib.my_requests import MyRequests
from lib.test_Data import TestData
from lib.context import Context
from lib.schema_validator import compare_json_structure

import allure


# 从 Excel 读取所有测试数据
test_data = TestData.get_all("APIInfo.xlsx", "asserts")


def extract_value(data, path):
    """
    按路径从嵌套JSON中提取值，支持任意层级

    path 示例:
      "data"                → data["data"]
      "entries.0.stream_id" → data["entries"][0]["stream_id"]
      "result.list.0.id"    → data["result"]["list"][0]["id"]
      "a.b.c.d.e"           → 任意深度嵌套
    """
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, list) and key.isdigit():
            value = value[int(key)]
        elif isinstance(value, dict):
            value = value[key]
        else:
            raise ValueError(f"路径 '{path}' 无法在响应中定位，在 '{key}' 处失败，当前值类型: {type(value).__name__}")
    return value


def replace_placeholders(text):
    """
    替换字符串中的 ${xxx} 占位符为 Context 中的实际值

    例如: {"entities":["${add_asset_id}"]}
    替换后: {"entities":["69d7644b0e1e723753ee6875"]}
    """
    def _replacer(match):
        key = match.group(1)
        value = Context.get(key)
        if value is None:
            raise ValueError(f"上下文中找不到变量: {key}，请确认前置用例已执行成功")
        return str(value)

    return re.sub(r'\$\{(\w+)\}', _replacer, text)


@pytest.mark.parametrize(
    "case",
    test_data,
    ids=[f"Case_{d.get('test_num', i)}-{d.get('test_name', '')}"
         for i, d in enumerate(test_data)]
)
@allure.feature("资产模块")
def test_asserts(case, logger):
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
        case_response = case.get('response')

        # ✅ 替换占位符 ${xxx} 为上下文中的实际值
        if case_params and '${' in case_params:
            logger.info(f"替换前参数: {case_params}")
            case_params = replace_placeholders(case_params)
            logger.info(f"替换后参数: {case_params}")

        reqParam = json.JSONDecoder().decode(case_params)
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
        response_type = case.get('response_type', 'json')  # 默认json
        #导出接口是个文件
        if response_type == 'file':
            # ===== 文件导出类接口的断言 =====

            # 1. 状态码断言
            assert res.status_code == 200, \
                f"请求失败，期望状态码200，实际: {res.status_code}"

            # 2. Content-Type 断言
            content_type = res.headers.get('Content-Type', '')
            valid_types = [
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/octet-stream'
            ]
            assert any(t in content_type for t in valid_types), \
                f"Content-Type 不是文件类型: {content_type}"
            logger.info(f"Content-Type 校验通过: {content_type}")

            # 3. Content-Disposition 断言（验证有文件名）
            content_disposition = res.headers.get('Content-Disposition', '')
            assert content_disposition, "响应头缺少 Content-Disposition"
            logger.info(f"Content-Disposition: {content_disposition}")

            # 4. 文件内容不为空
            assert len(res.content) > 0, "导出文件内容为空"
            logger.info(f"导出文件大小: {len(res.content)} 字节")

            # 5. 文件格式校验（验证是真正的 XLS/XLSX 文件）
            xls_magic = b'\xd0\xcf\x11\xe0'   # .xls (OLE2格式)
            xlsx_magic = b'\x50\x4b\x03\x04'  # .xlsx (ZIP格式)
            file_head = res.content[:4]
            assert file_head == xls_magic or file_head == xlsx_magic, \
                f"文件头校验失败，不是有效的 Excel 文件，文件头: {file_head.hex()}"
            logger.info("文件格式校验通过，是有效的 Excel 文件")

            # 6. 附加到 allure 报告
            allure.attach(
                f"Content-Type: {content_type}\n"
                f"Content-Disposition: {content_disposition}\n"
                f"文件大小: {len(res.content)} 字节",
                name="导出文件信息",
                attachment_type=allure.attachment_type.TEXT
            )
            logger.info("文件导出断言全部通过")

        else:
            # ===== JSON 接口断言 =====
            assert res.status_code == 200, \
                f"请求失败，期望状态码200，实际状态码: {res.status_code}，响应: {res.text}"
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

                # 记录到 allure 报告
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

    # ✅ 如果 Excel 中配置了 save_as，则将响应中指定字段保存到上下文
    # save_as: 变量名（存什么名字）
    # save_field: 从响应JSON中取哪个字段
    save_as = case.get('save_as')
    if save_as and response_type != 'file':
        save_field = case.get('save_field') or 'data'
        save_value = extract_value(res_json, save_field)
        Context.set(save_as, save_value)
        logger.info(f"已保存上下文: {save_as} = {save_value}（来自路径: {save_field}）")
        allure.attach(f"{save_as} = {save_value}（来自响应路径: {save_field}）", name="保存上下文变量", attachment_type=allure.attachment_type.TEXT)

    logger.info("测试完成"+case.get('test_name')+"接口")



if __name__ == '__main__':
    pytest.main([__file__, "-v", "-s"])

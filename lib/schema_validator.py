"""
JSON 结构校验工具模块

功能：递归提取 JSON 的 key 结构，对比两个 JSON 的结构是否一致（只比 key，不比值）

使用方式：
    在 Excel 的 response 字段中直接粘贴接口返回的完整 JSON（带真实数据），
    代码会自动提取两边的 key 结构进行对比。
"""


def extract_keys(data, path="root"):
    """
    递归提取 JSON 的所有 key 路径（结构）

    返回一个 set，包含所有 key 的完整路径，例如:
    输入: {"code": 200, "data": {"total": 10, "list": [{"id": "abc", "name": "test"}]}}
    输出: {"root.code", "root.data", "root.data.total", "root.data.list", "root.data.list[].id", "root.data.list[].name"}
    """
    keys = set()
    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{path}.{key}"
            keys.add(full_path)
            # 递归处理嵌套
            keys.update(extract_keys(value, full_path))
    elif isinstance(data, list):
        if len(data) > 0:
            # 只取第一个元素作为结构模板
            keys.update(extract_keys(data[0], f"{path}[]"))
    return keys


def compare_json_structure(actual_json, expected_json):
    """
    比较实际返回的 JSON 和期望的 JSON 的 key 结构是否一致

    返回: (is_pass, missing_keys, extra_keys)
      - is_pass: 布尔值，结构是否匹配
      - missing_keys: 实际响应中缺少的 key（期望有但实际没有）
      - extra_keys: 实际响应中多出的 key（实际有但期望没有）
    """
    actual_keys = extract_keys(actual_json)
    expected_keys = extract_keys(expected_json)

    missing_keys = expected_keys - actual_keys  # 期望有但实际没有
    extra_keys = actual_keys - expected_keys    # 实际有但期望没有

    is_pass = len(missing_keys) == 0  # 只要期望的 key 都存在就算通过

    return is_pass, missing_keys, extra_keys

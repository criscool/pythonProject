# -*- coding: utf-8 -*-
"""
用例间数据传递的全局上下文
用于接口关联场景：前一个接口的响应数据作为后一个接口的请求参数
"""


class Context:
    """
    全局上下文存储，支持用例间数据传递

    使用示例:
        # 保存数据（在添加接口的用例中）
        Context.set("add_asset_id", "69d7644b0e1e723753ee6875")

        # 读取数据（在删除接口的用例中）
        asset_id = Context.get("add_asset_id")

        # 清除所有数据
        Context.clear()
    """
    _data = {}

    @classmethod
    def set(cls, key, value):
        """保存数据到上下文"""
        cls._data[key] = value

    @classmethod
    def get(cls, key, default=None):
        """从上下文获取数据"""
        return cls._data.get(key, default)

    @classmethod
    def clear(cls):
        """清除所有上下文数据"""
        cls._data.clear()

    @classmethod
    def show(cls):
        """打印当前上下文内容（调试用）"""
        if not cls._data:
            print("📭 上下文为空")
            return
        print("📦 当前上下文:")
        for k, v in cls._data.items():
            print(f"   ├── {k} = {v}")

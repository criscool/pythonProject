# lib/test_data.py


from typing import Dict, List, Optional

from lib.excel_reader import ExcelReader


class TestData:
    """
    统一管理测试数据
    - 支持多个 xlsx 文件、多个 Sheet
    - 自动缓存，同一文件同一 Sheet 只读一次
    """

    _cache: Dict[str, any] = {}

    # ⭐ 统一配置 testData 目录前缀，只需改这一处
    DATA_DIR = "testData"

    @classmethod
    def _build_key(cls, file_name: str, sheet_name: str) -> str:
        """生成缓存 key"""
        return f"{file_name}::{sheet_name}"

    @classmethod
    def _read_excel(cls, file_name: str, sheet_name: str) -> List[dict]:
        """
        ⭐ 对接你的 ExcelReader
        """
        # 拼接路径：testData/eventsInfo.xlsx
        file_path = f"{cls.DATA_DIR}/{file_name}"
        reader = ExcelReader(file_path, sheet_name=sheet_name)
        data = reader.get_data()
        reader.close()
        return data

    @classmethod
    def get_one(cls, file_name: str, sheet_name: str) -> dict:
        """
        获取指定文件指定 Sheet 的第一行数据

        :param file_name: 文件名，如 "eventsInfo.xlsx"
        :param sheet_name: Sheet名，如 "eventsserach"
        :return: dict
        """
        key = cls._build_key(file_name, sheet_name)

        if key not in cls._cache:
            print(f"首次读取: {file_name} -> {sheet_name}")
            data = cls._read_excel(file_name, sheet_name)
            cls._cache[key] = data[0] if data else {}
        else:
            print(f"命中缓存: {file_name} -> {sheet_name}")

        return cls._cache[key]

    @classmethod
    def get_all(cls, file_name: str, sheet_name: str) -> List[dict]:
        """
        获取指定文件指定 Sheet 的所有数据

        :return: List[dict]
        """
        key = cls._build_key(file_name, sheet_name) + "::all"

        if key not in cls._cache:
            print(f"首次读取(全部): {file_name} -> {sheet_name}")
            cls._cache[key] = cls._read_excel(file_name, sheet_name)
        else:
            print(f"命中缓存(全部): {file_name} -> {sheet_name}")

        return cls._cache[key]

    @classmethod
    def get_value(cls, file_name: str, sheet_name: str, field: str) -> Optional[str]:
        """
        直接获取某个字段的值（取第一行）

        :param field: 字段名（Excel表头名）
        :return: 字段值
        """
        row = cls.get_one(file_name, sheet_name)
        value = row.get(field)
        if value is None:
            print(f"⚠️ 字段 '{field}' 不存在于 {file_name} -> {sheet_name}")
        return value

    @classmethod
    def get_row(cls, file_name: str, sheet_name: str, index: int) -> dict:
        """
        获取指定行的数据（从0开始）

        :param index: 行索引，0=第一行数据
        :return: dict
        """
        all_data = cls.get_all(file_name, sheet_name)
        if index >= len(all_data):
            print(f"⚠️ 索引 {index} 超出范围，共 {len(all_data)} 行数据")
            return {}
        return all_data[index]

    @classmethod
    def clear_cache(cls, file_name: str = None, sheet_name: str = None):
        """清除缓存"""
        if file_name and sheet_name:
            key = cls._build_key(file_name, sheet_name)
            cls._cache.pop(key, None)
            cls._cache.pop(key + "::all", None)
            print(f"🗑️ 已清除缓存: {file_name} -> {sheet_name}")
        else:
            cls._cache.clear()
            print("🗑️ 已清除所有缓存")

    @classmethod
    def show_cache(cls):
        """查看当前缓存情况"""
        if not cls._cache:
            print("📭 缓存为空")
            return
        print("📦 当前缓存:")
        for key in cls._cache:
            print(f"   ├── {key}")
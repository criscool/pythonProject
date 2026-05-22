from typing import Dict, List, Optional

from automation.core.data.loaders.excel_reader import ExcelReader
from automation.core.utils.path import get_testdata_dir


class TestData:
    """
    统一管理测试数据
    - 支持多个 xlsx 文件、多个 Sheet
    - 自动缓存，同一文件同一 Sheet 只读一次
    """

    _cache: Dict[str, any] = {}

    DATA_DIR = str(get_testdata_dir())

    @classmethod
    def _build_key(cls, file_name: str, sheet_name: str) -> str:
        return f"{file_name}::{sheet_name}"

    @classmethod
    def _read_excel(cls, file_name: str, sheet_name: str) -> List[dict]:
        file_path = f"{cls.DATA_DIR}/{file_name}"
        reader = ExcelReader(file_path, sheet_name=sheet_name)
        data = reader.get_data()
        reader.close()
        return data

    @classmethod
    def get_one(cls, file_name: str, sheet_name: str) -> dict:
        key = cls._build_key(file_name, sheet_name)

        if key not in cls._cache:
            data = cls._read_excel(file_name, sheet_name)
            cls._cache[key] = data[0] if data else {}
        return cls._cache[key]

    @classmethod
    def get_all(cls, file_name: str, sheet_name: str) -> List[dict]:
        key = cls._build_key(file_name, sheet_name) + "::all"

        if key not in cls._cache:
            cls._cache[key] = cls._read_excel(file_name, sheet_name)
        return cls._cache[key]

    @classmethod
    def get_value(cls, file_name: str, sheet_name: str, field: str) -> Optional[str]:
        row = cls.get_one(file_name, sheet_name)
        value = row.get(field)
        if value is None:
            print(f"⚠️ 字段 '{field}' 不存在于 {file_name} -> {sheet_name}")
        return value

    @classmethod
    def get_row(cls, file_name: str, sheet_name: str, index: int) -> dict:
        all_data = cls.get_all(file_name, sheet_name)
        if index >= len(all_data):
            return {}
        return all_data[index]

    @classmethod
    def clear_cache(cls, file_name: str = None, sheet_name: str = None):
        if file_name and sheet_name:
            key = cls._build_key(file_name, sheet_name)
            cls._cache.pop(key, None)
            cls._cache.pop(key + "::all", None)
        else:
            cls._cache.clear()

    @classmethod
    def show_cache(cls):
        if not cls._cache:
            print("缓存为空")
            return
        print("当前缓存:")
        for key in cls._cache:
            print(f"  ├── {key}")

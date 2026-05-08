# -*- coding: utf-8 -*-
"""
Excel文件读取工具类
用于读取testData目录下的xlsx文件，获取sheet名称和表格字段数据
"""
import os
import openpyxl


class ExcelReader:
    """
    Excel读取类，用于读取xlsx文件指定sheet的信息和表格数据。
    在创建实例时指定sheet名称，后续所有操作都针对该sheet。

    使用示例:
        # 只需传文件名，自动从testData目录读取
        reader1 = ExcelReader("eventsInfo.xlsx", sheet_name="eventsserach")
        print(reader1.get_sheet_name())
        print(reader1.get_headers())
        print(reader1.get_data())

        # 读取第二个sheet
        reader2 = ExcelReader("eventsInfo.xlsx", sheet_name="eventsdelete")
        print(reader2.get_headers())
        print(reader2.get_data())
    """

    def __init__(self, file_path, sheet_name=None):
        """
        初始化ExcelReader

        :param file_path: xlsx文件路径，支持相对路径和绝对路径
        :param sheet_name: 要操作的sheet名称，不传则默认使用第一个sheet
        """
        # 如果是相对路径，则基于项目根目录拼接
        if not os.path.isabs(file_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        self.file_path = file_path
        self.workbook = openpyxl.load_workbook(self.file_path)

        # 根据sheet_name获取对应的sheet
        if sheet_name is None:
            self.sheet = self.workbook.worksheets[0]
        else:
            if sheet_name not in self.workbook.sheetnames:
                raise ValueError(
                    f"Sheet '{sheet_name}' 不存在，可用的Sheet: {self.workbook.sheetnames}"
                )
            self.sheet = self.workbook[sheet_name]

    def get_all_sheet_names(self):
        """
        获取所有sheet的名称列表

        :return: sheet名称列表，如 ['eventsserach', 'Sheet2', ...]
        """
        return self.workbook.sheetnames

    def get_sheet_name(self):
        """
        获取当前sheet的名称

        :return: sheet的名称字符串
        """
        return self.sheet.title

    def get_headers(self):
        """
        获取当前sheet的字段名（第一行表头）

        :return: 字段名列表，如 ['test_num', 'test_name', 'params', ...]
        """
        headers = []
        for cell in self.sheet[1]:
            if cell.value is not None:
                headers.append(cell.value)
        return headers

    def get_data(self):
        """
        获取当前sheet中所有有效数据行（跳过表头和空行），以字典列表形式返回

        :return: 字典列表，每个字典的key为字段名，value为对应单元格的值
        例如: [{'test_num': '001', 'test_name': '搜索', ...}, ...]
        """
        headers = self.get_headers()
        data_list = []

        for row in self.sheet.iter_rows(min_row=2, max_row=self.sheet.max_row,
                                        max_col=len(headers)):
            row_values = [cell.value for cell in row]
            # 跳过全为空的行
            if all(v is None for v in row_values):
                continue
            row_dict = dict(zip(headers, row_values))
            data_list.append(row_dict)

        return data_list

    def get_column_data(self, column_name):
        """
        根据字段名获取当前sheet中该列的所有数据

        :param column_name: 字段名
        :return: 该列数据列表（不含表头，跳过None值）
        """
        headers = self.get_headers()
        if column_name not in headers:
            raise ValueError(f"字段名 '{column_name}' 不存在，可用字段: {headers}")

        col_index = headers.index(column_name) + 1  # openpyxl列索引从1开始
        column_data = []

        for row in self.sheet.iter_rows(min_row=2, max_row=self.sheet.max_row,
                                        min_col=col_index, max_col=col_index):
            value = row[0].value
            if value is not None:
                column_data.append(value)

        return column_data

    def close(self):
        """关闭工作簿"""
        self.workbook.close()

    def __del__(self):
        """析构时自动关闭工作簿"""
        try:
            self.workbook.close()
        except Exception:
            pass




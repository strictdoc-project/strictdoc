from enum import Enum
from typing import List

import openpyxl
import xlrd

from strictdoc.helpers.auto_described import auto_described


class ExcelLibType(Enum):
    XLRD = 1
    OPENPYXL = 2


@auto_described
class ExcelSheetProxy:
    """This proxy class allows to open either xls(xlrd) or xlsx(openpyxl) with the same interface"""

    def __init__(self, file: str):
        self.file = file
        if file.endswith(".xlsx"):
            self.workbook = openpyxl.load_workbook(file)
            self.sheet = self.workbook.active
            if self.sheet is None:
                raise RuntimeError(
                    "Couldn't open the first sheet of the workbook"
                )
            self.lib = ExcelLibType.OPENPYXL
        elif file.endswith(".xls"):
            self.workbook = xlrd.open_workbook(file, on_demand=True)
            self.sheet = self.workbook.sheet_by_index(0)
            self.lib = ExcelLibType.XLRD
        else:
            raise ValueError("Unsupported file format")

    @property
    def name(self) -> str:
        """returns the name of the first sheet"""
        if self.lib == ExcelLibType.OPENPYXL:
            return str(self.sheet.title)
        elif self.lib == ExcelLibType.XLRD:
            return str(self.sheet.name)
        return ""

    @property
    def ncols(self) -> int:
        """the number of columns"""
        ncols: int = 0
        if self.lib == ExcelLibType.OPENPYXL:
            ncols = self.sheet.max_column
        elif self.lib == ExcelLibType.XLRD:
            ncols = self.sheet.ncols
        return ncols

    @property
    def nrows(self) -> int:
        """the number of rows"""
        nrows: int = 0
        if self.lib == ExcelLibType.OPENPYXL:
            nrows = self.sheet.max_row
        elif self.lib == ExcelLibType.XLRD:
            nrows = self.sheet.nrows
        return nrows

    def get_cell_value(self, row: int, col: int) -> str:
        """returns the value at row/col as string"""
        cell_value: str = ""
        if self.lib == ExcelLibType.OPENPYXL:
            cell_value = (
                self.sheet.cell(row=row + 1, column=col + 1).value or ""
            )
        elif self.lib == ExcelLibType.XLRD:
            cell_value = self.sheet.cell_value(row, col)
        return cell_value

    def row_values(self, row: int) -> List[str]:
        """returns a full row as list"""
        row_values: List[str] = []
        if self.lib == ExcelLibType.OPENPYXL:
            row_values = [(cell.value or "") for cell in self.sheet[row + 1]]
        elif self.lib == ExcelLibType.XLRD:
            row_values = self.sheet.row_values(row)
        return row_values

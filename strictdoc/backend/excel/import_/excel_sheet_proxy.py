from typing import List

import openpyxl
import xlrd

from strictdoc.helpers.auto_described import auto_described


@auto_described
class ExcelSheetProxy:
    """This proxy class allows to open either xls(xlrd) or xlsx(openpyxl) with the same interface"""

    def __init__(self, file: str):
        self.file = file
        if file.endswith(".xlsx"):
            self.workbook = openpyxl.load_workbook(file)
            self.sheet = self.workbook.active
            self.lib = "openpyxl"
        elif file.endswith(".xls"):
            self.workbook = xlrd.open_workbook(file, on_demand=True)
            self.sheet = self.workbook.sheet_by_index(0)
            self.lib = "xlrd"
        else:
            raise ValueError("Unsupported file format")

    def name(self) -> str:
        """returns the name of the first sheet"""
        if self.lib == "openpyxl":
            return str(self.sheet.title)
        elif self.lib == "xlrd":
            return str(self.sheet.name)
        return ""

    def ncols(self) -> int:
        """returns the number of columns"""
        ncols: int = 0
        if self.lib == "openpyxl":
            ncols = self.sheet.max_column
        elif self.lib == "xlrd":
            ncols = self.sheet.ncols
        return ncols

    def nrows(self) -> int:
        """returns the number of rows"""
        nrows: int = 0
        if self.lib == "openpyxl":
            nrows = self.sheet.max_row
        elif self.lib == "xlrd":
            nrows = self.sheet.nrows
        return nrows

    def get_cell_value(self, row: int, col: int) -> str:
        """returns the value at row/col as string"""
        cell_value: str = ""
        if self.lib == "openpyxl":
            cell_value = (
                self.sheet.cell(row=row + 1, column=col + 1).value or ""
            )
        elif self.lib == "xlrd":
            cell_value = self.sheet.cell_value(row, col)
        return cell_value

    def row_values(self, row: int) -> List[str]:
        """returns a full row as list"""
        row_values: List[str] = []
        if self.lib == "openpyxl":
            row_values = [(cell.value or "") for cell in self.sheet[row + 1]]
        elif self.lib == "xlrd":
            row_values = self.sheet.row_values(row)
        return row_values

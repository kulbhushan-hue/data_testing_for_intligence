"""
Compatibility Database Helper Module
"""
import os
import pandas as pd

class CompatibilityDB:
    def __init__(self, excel_path: str = "ISV Compatibility assessment -Data.xlsx"):
        self.excel_path = excel_path

    def load(self) -> pd.DataFrame:
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"File not found: {self.excel_path}")
        df = pd.read_excel(self.excel_path, sheet_name="AMXT")
        return df

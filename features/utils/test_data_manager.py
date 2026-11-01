"""Test data loading utilities for multiple file formats."""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

import yaml

from features.utils.log_manager import get_logger


logger = get_logger(__name__)


class TestDataManager:
    """Load test data from various file formats."""

    def __init__(self, data_dir: str = "features/test_data"):
        """
        Initialize TestDataManager.

        Args:
            data_dir (str): Directory containing test data files
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            logger.warning(f"Test data directory not found: {self.data_dir}")

    def load_json(self, filename: str) -> Any:
        """
        Load data from JSON file.

        Args:
            filename (str): JSON filename

        Returns:
            Any: Parsed JSON data (dict or list)

        Example:
            data = TestDataManager().load_json("users.json")
            # Returns: {"users": [...]}
        """
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON data: {filename}")
            return data
        except FileNotFoundError:
            logger.error(f"JSON file not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            raise

    def load_yaml(self, filename: str) -> Any:
        """
        Load data from YAML file.

        Args:
            filename (str): YAML filename

        Returns:
            Any: Parsed YAML data (dict or list)

        Example:
            data = TestDataManager().load_yaml("users.yml")
            # Returns: {"users": [...]}
        """
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            logger.info(f"Loaded YAML data: {filename}")
            return data
        except FileNotFoundError:
            logger.error(f"YAML file not found: {filepath}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {filename}: {e}")
            raise

    def load_csv(self, filename: str) -> List[Dict[str, str]]:
        """
        Load data from CSV file.

        Args:
            filename (str): CSV filename

        Returns:
            List[Dict]: List of dictionaries (rows)

        Example:
            data = TestDataManager().load_csv("users.csv")
            # Returns: [{"name": "John", "email": "john@example.com"}, ...]
        """
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            logger.info(f"Loaded CSV data: {filename} ({len(data)} rows)")
            return data
        except FileNotFoundError:
            logger.error(f"CSV file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV {filename}: {e}")
            raise

    def load_excel(self, filename: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load data from Excel file.

        Args:
            filename (str): Excel filename (.xlsx or .xls)
            sheet_name (str, optional): Sheet name to load (default: first sheet)

        Returns:
            List[Dict]: List of dictionaries (rows)

        Example:
            data = TestDataManager().load_excel("users.xlsx", sheet_name="Users")
            # Returns: [{"name": "John", "email": "john@example.com"}, ...]
        """
        try:
            import openpyxl
            from openpyxl.utils import get_column_letter
        except ImportError:
            logger.error("openpyxl not installed. Install with: pip install openpyxl")
            raise ImportError("openpyxl required for Excel support")

        filepath = self.data_dir / filename
        try:
            wb = openpyxl.load_workbook(filepath)

            # Use specified sheet or first sheet
            if sheet_name:
                if sheet_name not in wb.sheetnames:
                    raise ValueError(f"Sheet '{sheet_name}' not found. Available: {wb.sheetnames}")
                ws = wb[sheet_name]
            else:
                ws = wb.active
                sheet_name = ws.title

            # Extract headers from first row
            headers = []
            for cell in ws[1]:
                if cell.value is not None:
                    headers.append(str(cell.value))

            # Extract data rows
            data = []
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
                row_data = {}
                for col_idx, cell in enumerate(row):
                    if col_idx < len(headers):
                        value = cell.value
                        # Normalize NaN and float values
                        if value is not None:
                            row_data[headers[col_idx]] = self._normalize_value(value)
                        else:
                            row_data[headers[col_idx]] = ""

                # Only add rows that have at least one non-empty value
                if any(row_data.values()):
                    data.append(row_data)

            logger.info(f"Loaded Excel data: {filename} (sheet: {sheet_name}, {len(data)} rows)")
            wb.close()
            return data

        except FileNotFoundError:
            logger.error(f"Excel file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error reading Excel {filename}: {e}")
            raise

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        """
        Normalize values (handle NaN, convert floats to int if appropriate).

        Args:
            value: Value to normalize

        Returns:
            Normalized value
        """
        # Handle NaN
        try:
            if isinstance(value, float):
                if value != value:  # NaN check
                    return ""
                # Convert float to int if it's a whole number
                if value.is_integer():
                    return int(value)
        except (TypeError, ValueError):
            pass

        return value

    def load(self, filename: str, **kwargs) -> Any:
        """
        Auto-detect file format and load data.

        Args:
            filename (str): Data filename
            **kwargs: Format-specific arguments (e.g., sheet_name for Excel)

        Returns:
            Loaded data

        Example:
            data = TestDataManager().load("users.json")
            data = TestDataManager().load("users.xlsx", sheet_name="Users")
            data = TestDataManager().load("users.csv")
            data = TestDataManager().load("users.yml")
        """
        filepath = self.data_dir / filename
        ext = filepath.suffix.lower()

        if ext == '.json':
            return self.load_json(filename)
        elif ext in ['.yml', '.yaml']:
            return self.load_yaml(filename)
        elif ext == '.csv':
            return self.load_csv(filename)
        elif ext in ['.xlsx', '.xls']:
            return self.load_excel(filename, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def get_test_cases(self, filename: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Load test cases from data file and convert to list of dicts.

        Args:
            filename (str): Test data filename
            **kwargs: Format-specific arguments

        Returns:
            List of test case dictionaries

        Example:
            test_cases = TestDataManager().get_test_cases("user_scenarios.csv")
            for case in test_cases:
                # case = {"username": "john", "email": "john@example.com", ...}
        """
        data = self.load(filename, **kwargs)

        # If it's already a list, return it
        if isinstance(data, list):
            return data

        # If it's a dict with a single key that's a list, return that list
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    return value

        # Single dict, wrap in list
        return [data]

    def filter_test_cases(
        self,
        filename: str,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Load test cases and filter by criteria.

        Args:
            filename (str): Test data filename
            **filters: Column=value pairs to filter by

        Returns:
            Filtered test cases

        Example:
            # Get only active users
            cases = TestDataManager().filter_test_cases("users.csv", status="active")
            
            # Get users from specific role
            cases = TestDataManager().filter_test_cases("users.json", role="admin")
        """
        test_cases = self.get_test_cases(filename)
        filtered = []

        for case in test_cases:
            match = True
            for key, value in filters.items():
                if key not in case or str(case[key]) != str(value):
                    match = False
                    break
            if match:
                filtered.append(case)

        logger.info(f"Filtered {len(test_cases)} cases to {len(filtered)} matching cases")
        return filtered

    def slice_test_cases(
        self,
        filename: str,
        start_index: int = 0,
        end_index: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Load test cases and slice by index range.

        Args:
            filename (str): Test data filename
            start_index (int): Start index (inclusive)
            end_index (int, optional): End index (exclusive)
            **kwargs: Format-specific arguments

        Returns:
            Sliced test cases

        Example:
            # Get first 10 test cases
            cases = TestDataManager().slice_test_cases("users.csv", start_index=0, end_index=10)
            
            # Get cases 100-200
            cases = TestDataManager().slice_test_cases("users.csv", start_index=100, end_index=200)
        """
        test_cases = self.get_test_cases(filename, **kwargs)
        sliced = test_cases[start_index:end_index]
        logger.info(f"Sliced {len(test_cases)} cases to {len(sliced)} cases")
        return sliced

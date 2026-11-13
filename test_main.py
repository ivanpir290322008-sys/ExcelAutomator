import unittest
import pandas as pd
from unittest.mock import patch
import tempfile
from pathlib import Path
from main import merge_tables, sort_table, load_excel_files


class TestExcelAutomator(unittest.TestCase):

    def test_merge_tables(self):
        table1 = pd.DataFrame({
            "ID": [1, 2],
            "Имя": ["Анна", "Иван"]
        })

        table2 = pd.DataFrame({
            "ID": [2, 3],
            "Имя": ["Иван", "Олег"]
        })

        result = merge_tables([table1, table2])

        self.assertEqual(result["ID"].tolist(), [1, 2, 3])

    def test_merge_without_duplicates(self):
        table1 = pd.DataFrame({
            "ID": [1, 2],
            "Имя": ["Анна", "Иван"]
        })

        table2 = pd.DataFrame({
            "ID": [3, 4],
            "Имя": ["Иван", "Олег"]
        })

        result = merge_tables([table1, table2])

        self.assertEqual(result["ID"].tolist(), [1, 2, 3, 4])


    def test_sort_ascending(self):
        table = pd.DataFrame({
            "ID": [3, 1, 2],
            "Имя": ["Олег", "Анна", "Иван"]
        })

        # Имитируем два ответа пользователя
        with patch("builtins.input", side_effect=["ID", "1"]):
            result = sort_table(table)

        # Проверяем порядок ID
        self.assertEqual(result["ID"].tolist(), [1, 2, 3])

    def test_sort_descending(self):
        table = pd.DataFrame({
            "ID": [2, 3, 1],
            "Имя": ["Иван", "Олег", "Анна"]
        })

        with patch("builtins.input", side_effect=["ID", "2"]):
            result = sort_table(table)

        self.assertEqual(result["ID"].tolist(), [3, 2, 1])

    def test_sort_invalid_input(self):
        table = pd.DataFrame({
            "ID": [3, 1, 2]
        })

        with patch("builtins.input", side_effect=["ошибка", "ID", "5", "1"]):
            result = sort_table(table)

        self.assertEqual(result["ID"].tolist(), [1, 2, 3])
    
    def test_load_excel_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            table1 = pd.DataFrame({
                "ID": [1, 2],
                "Имя": ["Анна", "Иван"]
            })

            table2 = pd.DataFrame({
                "ID": [3, 4],
                "Имя": ["Олег", "Мария"]
            })

            table1.to_excel(folder / "table1.xlsx", index=False)
            table2.to_excel(folder / "table2.xlsx", index=False)

            tables, failed_files = load_excel_files(folder)

            self.assertEqual(len(tables), 2)
            self.assertEqual(len(failed_files), 0)

    def test_load_damaged_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            table1 = pd.DataFrame({
                "ID": [1, 2],
                "Имя": ["Анна", "Иван"]
            })

            table1.to_excel(folder / "table1.xlsx", index=False)
            (folder / "damaged.xlsx").write_text("Это не Excel-файл", encoding="utf-8")

            tables, failed_files = load_excel_files(folder)

            self.assertEqual(len(tables), 1)
            self.assertEqual(len(failed_files), 1)

    def test_load_different_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            table1 = pd.DataFrame({
                "ID": [1, 2],
                "Имя": ["Анна", "Иван"]
            })

            table2 = pd.DataFrame({
                "ID": [3, 4],
                "Сумма": ["1500", "2700"]
            })

            table1.to_excel(folder / "table1.xlsx", index=False)
            table2.to_excel(folder / "table2.xlsx", index=False)

            with patch("builtins.print") as mock_print:
                with self.assertRaises(SystemExit):
                    load_excel_files(folder)

            mock_print.assert_called_with(
                "Ошибка структура таблиц не совпадает!",
                "table2.xlsx"
            )

    def test_load_reordered_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            table1 = pd.DataFrame({
                "ID": [1],
                "Имя": ["Анна"]
            })

            table2 = pd.DataFrame({
                "Имя": ["Иван"],
                "ID": [2]
            })

            table1.to_excel(folder / "table1.xlsx", index=False)
            table2.to_excel(folder / "table2.xlsx", index=False)
           
            tables, failed_files = load_excel_files(folder)

            self.assertEqual(len(tables), 2)
            self.assertEqual(len(failed_files), 0)
            self.assertEqual(list(tables[1].columns), ["ID", "Имя"])


if __name__ == "__main__":
    unittest.main()
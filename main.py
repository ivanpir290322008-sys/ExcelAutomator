import pandas as pd
from pathlib import Path

#Выбор по убыванию или возрастанию
def choose_sort_direction():
    while True:
        print("Сортировка по возрастанию - 1 или по убыванию - 2")
        choice = input("Введите 1 или 2: ").strip()

        if choice == "1":
            print("По возрастанию")
            return True
        elif choice == "2":
            print("По убыванию ")
            return False
        else:
            print("Неверный выбор")

#Загрузка таблиц
def load_excel_files(folder):
    # Найди все Excel-файлы
    files = sorted(folder.glob("*.xlsx"))

    # Создай пустой список
    tables = list()

    # Список файлов-ошибок
    failed_files = []

    #Структура таблицы
    expected_columns = None

    # Прочитай каждый файл и добавь таблицу в список
    for file in files:
        if file.name.startswith("~$"):
            continue

        try:
            # Прочитай Excel-файл
            df = pd.read_excel(file)

        except Exception as error:
            # Сохрани название проблемного файла и причину ошибки
            failed_files.append({
            "name": file.name,
            "error": str(error)
            })  

            # Заверши программу
            #raise SystemExit(1)
            continue

        #Получаем текущую структуру таблицы
        current_columns = list(df.columns)

        #Проверяем одинаковая ли структура во всех таблицах
        if expected_columns is None:
            expected_columns = current_columns

        elif sorted(expected_columns) != sorted(current_columns):
            print("Ошибка структура таблиц не совпадает!", file.name)
            raise SystemExit(1)

        #Иземеняем структуру таблицы, если там присутствует перестановка колон
        df = df[expected_columns]

        # Добавь таблицу в список
        tables.append(df)

    #Проверка на наличие Excel-файлов
    if not tables:
        print("Ошибка: в папке input нет Excel-файлов.")
        raise SystemExit(1)

    return tables, failed_files

def merge_tables(tables):
    # Объедини все таблицы
    result = pd.concat(tables, ignore_index=True)
    print("Загружен таблиц:", len(tables))
    rows_before = len(result)
    print("Строк до обработки: ", rows_before)

    #Удалить дубликаты
    result = result.drop_duplicates()
    print("Строк удалено: ", rows_before - len(result))
    print("Строк после обработки ", len(result))

    return result

def sort_table(result):
    #Получаем структуру колонн
    columns = list(result.columns)
    while True:
        #Объявляем ввод пользователем колонны для сортировки
        print("Доступные названия колонн", columns)
        sort_column = input("Введите название колонны по которой хотите отсортировать: ").strip()

        #Приведём к общему виду готовую структуру колонн
        for column in columns:
            if column.lower() == sort_column.lower():
                sort_column = column
                break

        #Проверка сущ. колонны для сортировки
        if sort_column not in columns:
            print("Ошибка такой колонны не существует!")

        else:
            break

    #Выбор сортировки по убыванию или возрастанию
    ascending = choose_sort_direction()

    #Отсортировать по выбранной пользователем колонне
    result = result.sort_values(by=sort_column, ascending=ascending)

    #Сброс индексов
    result = result.reset_index(drop=True)
    return result

def save_result(result, output_file):
    #Создай папку, если её нет
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Сохрани таблицу в result.xlsx
    try:
        result.to_excel(output_file, index=False)

    except PermissionError:
        print("Ошибка: закройте result.xlsx.")
        raise SystemExit(1)
        

    # Выведи сообщение
    print("Таблица успешно сохранена!")

def main():
    #Открываем папку с таблицами
    folder = Path("input")

    #Получаем таблицы, файлы с ошибками, структуру колонн
    tables, failed_files = load_excel_files(folder)

    #Объединяем таблицы
    result = merge_tables(tables)

    #Сортируем по выбранной колонне
    result = sort_table(result)

    #Создадим файл для результатов
    output_file = Path("output") / "result.xlsx"

    #Сохраняем результат в файле
    save_result(result, output_file)

    # Вывод ошибок при наличии
    if failed_files:
        print("ВНИМАНИЕ: Результат может быть неполным!")
        print("Пропущено файлов:", len(failed_files))
        for file_name in failed_files:
            print("-", "Название файла:", file_name["name"])
            print(" ", "Причина ошибки:", file_name["error"])

if __name__ == "__main__":
    main()
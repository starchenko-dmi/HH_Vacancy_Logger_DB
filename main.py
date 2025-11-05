# main.py
from config import DB_CONFIG, EMPLOYER_IDS
from src.api.hh_api import HeadHunterAPI
from src.db.db_creator import create_database, create_tables
from src.db.db_manager import DBManager
import psycopg2

def fill_database():
    """Заполняет БД данными с hh.ru."""
    api = HeadHunterAPI()
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for emp_id in EMPLOYER_IDS:
        print(f"Обработка компании ID: {emp_id}")
        emp_info = api.get_employer_info(emp_id)
        if not emp_info:
            continue

        # Сохраняем работодателя
        cur.execute("""
            INSERT INTO employers (employer_id, name, url, open_vacancies)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (employer_id) DO NOTHING
        """, (
            emp_info["id"],
            emp_info["name"],
            emp_info.get("alternate_url"),
            emp_info.get("open_vacancies", 0)
        ))

        # Получаем и сохраняем вакансии
        vacancies = api.get_vacancies_by_employer(emp_id)
        for v in vacancies:
            salary = v.get("salary") or {}
            cur.execute("""
                INSERT INTO vacancies (vacancy_id, employer_id, name, salary_from, salary_to, currency, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO NOTHING
            """, (
                v["id"],
                emp_id,
                v["name"],
                salary.get("from"),
                salary.get("to"),
                salary.get("currency"),
                v["alternate_url"]
            ))

    conn.commit()
    cur.close()
    conn.close()
    print("Данные успешно загружены в БД.")

def user_interface():
    """Интерфейс взаимодействия с пользователем."""
    db = DBManager(DB_CONFIG)
    while True:
        print("\nВыберите действие:")
        print("1. Список компаний и количество вакансий")
        print("2. Все вакансии")
        print("3. Средняя зарплата")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("Ваш выбор: ").strip()
        if choice == "1":
            data = db.get_companies_and_vacancies_count()
            for company, count in data:
                print(f"{company}: {count} вакансий")
        elif choice == "2":
            data = db.get_all_vacancies()
            for company, title, s_from, s_to, url in data:
                salary = f"от {s_from}" if s_from else ""
                salary += f" до {s_to}" if s_to else ""
                salary = salary or "не указана"
                print(f"{company} — {title} | {salary} | {url}")
        elif choice == "3":
            print(f"Средняя зарплата: {db.get_avg_salary()} руб.")
        elif choice == "4":
            data = db.get_vacancies_with_higher_salary()
            for company, title, s_from, s_to, url in data:
                print(f"{company} — {title} | от {s_from or '?'} до {s_to or '?'} | {url}")
        elif choice == "5":
            word = input("Введите ключевое слово: ").strip()
            data = db.get_vacancies_with_keyword(word)
            if not data:
                print("Ничего не найдено.")
            for company, title, s_from, s_to, url in data:
                print(f"{company} — {title} | {url}")
        elif choice == "0":
            break
        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    # Создание БД и таблиц
    create_database(DB_CONFIG)
    create_tables(DB_CONFIG)
    # Загрузка данных
    fill_database()
    # Запуск интерфейса
    user_interface()
# src/db/db_manager.py
import psycopg2
from typing import List, Tuple, Optional
from src.db.db_creator import create_database, create_tables
from config import DB_CONFIG

class DBManager:
    """Класс для работы с базой данных PostgreSQL."""

    def __init__(self, config: dict):
        self.config = config

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Получает список компаний и количество вакансий у каждой."""
        with psycopg2.connect(**self.config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.name, COUNT(v.vacancy_id)
                    FROM employers e
                    LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                    GROUP BY e.name
                    ORDER BY COUNT(v.vacancy_id) DESC
                """)
                return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """Получает все вакансии с названием компании, вакансии, зарплатой и ссылкой."""
        with psycopg2.connect(**self.config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                """)
                return cur.fetchall()

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям (среднее из (from + to)/2)."""
        with psycopg2.connect(**self.config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0)
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                """)
                result = cur.fetchone()[0]
                return round(result, 2) if result else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """Получает вакансии с зарплатой выше средней."""
        avg = self.get_avg_salary()
        with psycopg2.connect(**self.config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 > %s
                """, (avg,))
                return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """Получает вакансии, в названии которых есть ключевое слово."""
        with psycopg2.connect(**self.config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE LOWER(v.name) LIKE %s
                """, (f"%{keyword.lower()}%",))
                return cur.fetchall()
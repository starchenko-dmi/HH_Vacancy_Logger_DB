# src/db/db_creator.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Dict

def create_database(config: Dict[str, str]) -> None:
    """Создаёт базу данных, если её нет."""
    conn = psycopg2.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        port=config["port"]
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (config["database"],))
    exists = cur.fetchone()
    if not exists:
        cur.execute(f'CREATE DATABASE "{config["database"]}"')
    cur.close()
    conn.close()

def create_tables(config: Dict[str, str]) -> None:
    """Создаёт таблицы employers и vacancies."""
    conn = psycopg2.connect(**config)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employers (
            employer_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url TEXT,
            open_vacancies INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id VARCHAR(20) PRIMARY KEY,
            employer_id VARCHAR(20) REFERENCES employers(employer_id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            currency VARCHAR(10),
            url TEXT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
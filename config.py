# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "hh_vacancies"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432")
}

# Список ID интересующих компаний (можно заменить на другие)
EMPLOYER_IDS = [
    "1740",   # Яндекс
    "3529",   # Сбер
    "80",     # Альфа-Банк
    "2180",   # VK
    "1122462",# Тинькофф
    "15478",  # Ozon
    "78638",  # Avito
    "1429",   # МТС
    "1057",   # Газпром нефть
    "194231"  # Skyeng
]
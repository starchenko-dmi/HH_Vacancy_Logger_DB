# src/api/hh_api.py
import requests
import time
from typing import List, Dict, Optional

class HeadHunterAPI:
    """Класс для взаимодействия с API hh.ru."""

    def __init__(self):
        self._base_url = "https://api.hh.ru"
        self._headers = {"DM-Star": "HH_Vacancy_Logger_DB/1.0 (Starchenko.Dmitry@gmail.com)"}

    def get_employer_info(self, employer_id: str) -> Optional[Dict]:
        """Получает информацию о работодателе по ID."""
        try:
            response = requests.get(
                f"{self._base_url}/employers/{employer_id}",
                headers=self._headers,
                timeout=10
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def get_vacancies_by_employer(self, employer_id: str) -> List[Dict]:
        """Получает все вакансии работодателя (до 2000)."""
        vacancies = []
        page = 0
        while page < 20:  # максимум 2000 вакансий
            params = {"employer_id": employer_id, "per_page": 100, "page": page}
            try:
                response = requests.get(
                    f"{self._base_url}/vacancies",
                    headers=self._headers,
                    params=params,
                    timeout=10
                )
                if response.status_code != 200:
                    break
                data = response.json()
                items = data.get("items", [])
                if not items:
                    break
                vacancies.extend(items)
                page += 1
                time.sleep(0.2)
            except Exception:
                break
        return vacancies
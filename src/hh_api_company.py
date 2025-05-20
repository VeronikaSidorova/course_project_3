import time
from typing import Optional, List, Dict, Any, Tuple

import requests


class HHApi:
    """Класс для взаимодействия с API HeadHunter (hh.ru)."""
    BASE_URL = "https://api.hh.ru"
    HEADERS = {"User-Agent": "HH-User-Agent"}

    def __init__(self, delay: float = 0.5):
        self.delay = delay

    def get_company_id(self, company_name: str) -> Optional[str]:
        """Получает ID компании по названию."""
        params = {"text": company_name}
        response = requests.get(f"{self.BASE_URL}/employers", headers=self.HEADERS, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])
        for item in items:
            if item["name"].lower() == company_name.lower():
                return item["id"]
        return None

    def get_vacancies_by_company_id(self, employer_id: str) -> List[Dict[str, Any]]:
        """Получает список вакансий по ID работодателя."""
        vacancies = []
        page = 0
        while True:
            params = {"employer_id": employer_id, "per_page": 20, "page": page}
            response = requests.get(f"{self.BASE_URL}/vacancies", headers=self.HEADERS, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            vacancies.extend(items)
            if not data.get("more"):
                break
            page += 1
            time.sleep(self.delay)
        return vacancies

    @staticmethod
    def parse_salary(salary_data: Optional[Dict[str, Any]]) -> Tuple[Optional[int], Optional[int]]:
        """Парсит данные о зарплате из API."""
        if salary_data is None:
            return None, None
        salary_from = salary_data.get("from")
        salary_to = salary_data.get("to")
        return salary_from, salary_to

from typing import Any, List, Dict

import psycopg2

from src.config import config
from src.hh_api_company import HHApi


def create_database(db_name: str) -> None:
    """
    Создает новую базу данных с указанным именем.
    Если база данных с таким именем уже существует, команда DROP DATABASE удалит ее перед созданием новой.
    """
    # Создаем базу данных (если нужно)
    conn_params = config()
    conn = psycopg2.connect(dbname="postgres", **conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE {db_name}")
    cur.execute(f"CREATE DATABASE {db_name}")

    cur.close()
    conn.close()


def create_tables() -> None:
    """
    Создает таблицы 'companies' и 'vacancies' в базе данных 'vacancies_db', если они еще не существуют.
    Использует параметры подключения из конфигурационного файла.
    """
    params = config()
    with psycopg2.connect(dbname="vacancies_db", **params) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL
                );
            """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    salary_from NUMERIC,
                    salary_to NUMERIC,
                    url TEXT,
                    company_id INTEGER REFERENCES companies(id)
                );
            """
            )


def save_company_and_vacancies(
    db_manager: Any,
    company_name: str,
    vacancies: List[Dict[str, Any]]
) -> None:
    """
    Добавляет компанию и связанные вакансии в обе таблицы базы данных.
    """
    # Добавляем компанию и получаем её ID
    company_id = db_manager.add_company_in_db(company_name)

    # Для каждой вакансии добавляем запись
    for vac in vacancies:
        vac_name = vac["name"]
        salary_from, salary_to = HHApi.parse_salary(vac.get("salary"))
        url = vac["alternate_url"]
        db_manager.add_vacancy_in_db(vac_name, salary_from, salary_to, url, company_id)

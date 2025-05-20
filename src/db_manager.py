from typing import Optional, List, Tuple

import psycopg2

from src.config import config


class DBManager:
    """Класс для управления подключением и взаимодействием с базой данных PostgreSQL."""
    def __init__(self) -> None:
        self.cur = None
        self.conn_params = config()

    def __enter__(self) -> "DBManager":
        self.conn = psycopg2.connect(**self.conn_params)
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cur.close()
        self.conn.close()

    def add_company(self, name: str) -> int:
        """Добавляет компанию или возвращает существующий id."""
        self.cur.execute(
            "INSERT INTO companies (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;", (name,)
        )
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            # Если компания уже есть, получим ее id
            self.cur.execute("SELECT id FROM companies WHERE name=%s;", (name,))
            return self.cur.fetchone()[0]

    def add_vacancy(self,
        name: str,
        salary_from: Optional[float],
        salary_to: Optional[float],
        url: str,
        company_id: int
    ) -> None:
        """Добавляет вакансию."""
        self.cur.execute(
            """
            INSERT INTO vacancies (name, salary_from, salary_to, url, company_id)
            VALUES (%s,%s,%s,%s,%s);
            """,
            (name, salary_from, salary_to, url, company_id),
        )

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Возвращает список компаний и количество вакансий у каждой."""
        self.cur.execute(
            """
            SELECT c.name, COUNT(v.id) FROM companies c
            LEFT JOIN vacancies v ON c.id=v.company_id
            GROUP BY c.id;
        """
        )
        return self.cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[float], Optional[float], str]]:
        """Возвращает все вакансии с информацией о компании."""
        self.cur.execute(
            """
            SELECT c.name AS company_name,
                   v.name AS vacancy_name,
                   v.salary_from,
                   v.salary_to,
                   v.url
              FROM vacancies v JOIN companies c ON v.company_id=c.id;
        """
        )
        return self.cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        """Вычисляет среднюю зарплату по вакансиям."""
        self.cur.execute(
            """
            SELECT AVG((salary_from + salary_to)/2) 
            FROM vacancies WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL;
        """
        )
        result = self.cur.fetchone()[0]
        return result

    @property
    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, Optional[float], Optional[float], str]]:
        """Возвращает вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        self.cur.execute(
            """
            SELECT c.name AS company_name,
                   v.name AS vacancy_name,
                   v.salary_from,
                   v.salary_to,
                   v.url
              FROM vacancies v JOIN companies c ON v.company_id=c.id
             WHERE ((v.salary_from + v.salary_to)/2) > %s;
         """,
            (avg_salary,),
        )
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, Optional[float], Optional[float], str]]:
        """Возвращает вакансии по ключевому слову в названии."""
        pattern = f"%{keyword}%"
        self.cur.execute(
            """
            SELECT c.name AS company_name,
                   v.name AS vacancy_name,
                   v.salary_from,
                   v.salary_to,
                   v.url
              FROM vacancies v JOIN companies c ON v.company_id=c.id
             WHERE v.name ILIKE %s;
         """,
            (pattern,),
        )
        return self.cur.fetchall()

    def add_company_in_db(self, company_name: str) -> int:
        """
        Вставляет новую компанию в таблицу companies.
        Возвращает id вставленной записи.
        """
        self.cur.execute("INSERT INTO companies (name) VALUES (?)", (company_name,))
        return self.cur.lastrowid

    def add_vacancy_in_db(self, name: str, salary_from: Optional[float], salary_to: Optional[float], url: str, company_id: int) -> None:
        """
        Вставляет вакансию в таблицу vacancies.
        """
        self.cur.execute(
            """
            INSERT INTO vacancies (name, salary_from, salary_to, url, company_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, salary_from, salary_to, url, company_id),
        )

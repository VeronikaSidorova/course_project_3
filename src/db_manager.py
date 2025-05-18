import psycopg2

from src.config import config


class DBManager:
    def __init__(self):
        self.cursor = None
        self.conn_params = config()

    def __enter__(self):
        self.conn = psycopg2.connect(**self.conn_params)
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()

    def add_company(self, name):
        self.cur.execute(
            "INSERT INTO companies (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;",
            (name,)
        )
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            # Если компания уже есть, получим ее id
            self.cur.execute("SELECT id FROM companies WHERE name=%s;", (name,))
            return self.cur.fetchone()[0]

    def add_vacancy(self, name, salary_from, salary_to, url, company_id):
        self.cur.execute(
            """
            INSERT INTO vacancies (name, salary_from, salary_to, url, company_id)
            VALUES (%s,%s,%s,%s,%s);
            """,
            (name, salary_from, salary_to, url, company_id)
        )

    def get_companies_and_vacancies_count(self):
        self.cur.execute("""
            SELECT c.name, COUNT(v.id) FROM companies c
            LEFT JOIN vacancies v ON c.id=v.company_id
            GROUP BY c.id;
        """)
        return self.cur.fetchall()

    def get_all_vacancies(self):
        self.cur.execute("""
            SELECT c.name AS company_name,
                   v.name AS vacancy_name,
                   v.salary_from,
                   v.salary_to,
                   v.url
              FROM vacancies v JOIN companies c ON v.company_id=c.id;
        """)
        return self.cur.fetchall()

    def get_avg_salary(self):
        self.cur.execute("""
            SELECT AVG((salary_from + salary_to)/2) FROM vacancies WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL;
        """)
        result = self.cur.fetchone()[0]
        return result

    @property
    def get_vacancies_with_higher_salary(self):
        avg_salary = self.get_avg_salary()
        self.cur.execute("""
            SELECT c.name AS company_name,
                   v.name AS vacancy_name,
                   v.salary_from,
                   v.salary_to,
                   v.url
              FROM vacancies v JOIN companies c ON v.company_id=c.id
             WHERE ((v.salary_from + v.salary_to)/2) > %s;
         """, (avg_salary,))
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        pattern = f'%{keyword}%'
        self.cur.execute("""
            SELECT c.name AS company_name,
                   v.name AS vacancy_name,
                   v.salary_from,
                   v.salary_to,
                   v.url
              FROM vacancies v JOIN companies c ON v.company_id=c.id
             WHERE v.name ILIKE %s;
         """, (pattern,))
        return self.cur.fetchall()

    def add_company_in_db(self, company_name):
        """
        Вставляет новую компанию в таблицу companies.
        Возвращает id вставленной записи.
        """
        self.cursor.execute(
            "INSERT INTO companies (name) VALUES (?)",
            (company_name,)
        )
        return self.cursor.lastrowid

    def add_vacancy_in_db(self, name, salary_from, salary_to, url, company_id):
        """
        Вставляет вакансию в таблицу vacancies.
        """
        self.cursor.execute(
            """
            INSERT INTO vacancies (name, salary_from, salary_to, url, company_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, salary_from, salary_to, url, company_id)
        )
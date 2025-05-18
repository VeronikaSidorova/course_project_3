from config import config
from src.db_manager import DBManager
from src.db_script import create_database, create_tables, save_company_and_vacancies
from src.hh_api_company import HHApi


def main():

    with DBManager() as dbm:
        # Получение настроек базы данных (или других параметров)
        db_config = config()
        create_database("vacancies_db")
        create_tables()

        # Инициализация API клиента hh.ru
        hh_api = HHApi()

        companies_list = ["Google", "Microsoft", "Apple", "Amazon", "Yandex",
                          "Tesla", "Facebook", "Samsung", "Intel", "IBM"]
        for comp_name in companies_list:
            print(f"Обработка компании: {comp_name}")

            comp_id_in_api = hh_api.get_company_id(comp_name)

            if comp_id_in_api is None:
                print(f"Компания {comp_name} не найдена.")
                continue

            local_company_id = dbm.add_company(comp_name)

            vacancies = hh_api.get_vacancies_by_company_id(comp_id_in_api)

            for vac in vacancies:
                vac_name = vac['name']
                sal_from, sal_to = hh_api.parse_salary(vac.get('salary'))
                dbm.add_vacancy(
                    vac_name,
                    sal_from,
                    sal_to,
                    vac['alternate_url'],
                    local_company_id
                )


if __name__ == "__main__":
    main()
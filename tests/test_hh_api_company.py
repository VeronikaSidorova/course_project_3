import unittest
from unittest.mock import Mock, patch

from src.hh_api_company import HHApi


class TestHHApi(unittest.TestCase):

    @patch("src.hh_api_company.requests.get")
    def test_get_company_id_found(self, mock_get):
        # Мокаем ответ API с подходящим работодателем
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [{"id": "123", "name": "Test Company"}, {"id": "456", "name": "Another Company"}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = HHApi()
        company_id = api.get_company_id("Test Company")
        self.assertEqual(company_id, "123")
        mock_get.assert_called_with(f"{api.BASE_URL}/employers", headers=api.HEADERS, params={"text": "Test Company"})

    @patch("src.hh_api_company.requests.get")
    def test_get_company_id_not_found(self, mock_get):
        # Мокаем ответ API без подходящего работодателя
        mock_response = Mock()
        mock_response.json.return_value = {"items": [{"id": "123", "name": "Other Company"}]}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = HHApi()
        result = api.get_company_id("Nonexistent Company")
        self.assertIsNone(result)

    @patch("src.hh_api_company.requests.get")
    def test_get_vacancies_by_company_id_multiple_pages(self, mock_get):
        # Мокаем два вызова API для пагинации
        first_page_data = {"items": [{"id": "1"}, {"id": "2"}], "more": True}
        second_page_data = {"items": [{"id": "3"}], "more": False}

        # Настраиваем последовательность возвращаемых значений
        mock_response1 = Mock()
        mock_response1.json.return_value = first_page_data
        mock_response1.raise_for_status = Mock()

        mock_response2 = Mock()
        mock_response2.json.return_value = second_page_data
        mock_response2.raise_for_status = Mock()

        # Указываем, что при вызове requests.get возвращаются эти моки по очереди
        mock_get.side_effect = [mock_response1, mock_response2]

        api = HHApi(delay=0)  # отключаем задержку для теста
        vacancies = api.get_vacancies_by_company_id("123")

        self.assertEqual(len(vacancies), 3)
        self.assertEqual([v["id"] for v in vacancies], ["1", "2", "3"])

    def test_parse_salary_none(self):
        salary_from, salary_to = HHApi.parse_salary(None)
        self.assertIsNone(salary_from)
        self.assertIsNone(salary_to)

    def test_parse_salary_partial(self):
        salary_data_from_only = {"from": 1000}
        salary_data_to_only = {"to": 2000}

        from_val, to_val = HHApi.parse_salary(salary_data_from_only)
        self.assertEqual(from_val, 1000)
        self.assertIsNone(to_val)

        from_val, to_val = HHApi.parse_salary(salary_data_to_only)
        self.assertIsNone(from_val)

    def test_parse_salary_full(self):
        salary_data_full = {"from": 1000, "to": 2000}

        from_val, to_val = HHApi.parse_salary(salary_data_full)

        self.assertEqual(from_val, 1000)
        self.assertEqual(to_val, 2000)

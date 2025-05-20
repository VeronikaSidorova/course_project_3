# Проект 3

## Описание
Цель проекта заключается в получении данных о компаниях и вакансиях с сайта hh.ru, проектировании таблицы в БД PostgreSQL и загрузке полученных данные в созданные таблицы.

## Установка и использование
Клонируйте репозиторий
```
https://github.com/VeronikaSidorova/course_project_3
```
Для работы программы необходимо установить зависимости, указанные в файле requirements.txt
```
pip install -r requirements.txt
```
Для работы с базой данных необходимо создать файл .env с параметрами доступа к базе данных PostgresSQL. Пример содержимого файла:
```
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_PORT=5432
POSTGRES_DB=postgres
```
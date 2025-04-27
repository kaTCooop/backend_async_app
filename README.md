# Инструкция по запуску с docker-compose  
1. cd project_folder  
2. docker-compose up  
  
Сайт доступен по http://localhost:8000  
  
# Инструкция по запуску без docker-compose
1. python 3.9+
2. pip install sanic sqlalchemy sanic_jinja2 psycopg2

Устанавливаем переменную с ссылкой на созданную пустую базу данных postgreSQL, в которую будем вносить изменения  
(powershell)  
3. $env:DB_URL = "postgresql+psycopg2://user:password@localhost:port/database.db"  
(bash)  
3. export DB_URL = "postgresql+psycopg2://user:password@localhost:port/database.db"  
  
Например postgresql+psycopg2://postgres:postgres@localhost:5432/async_app.db  
  
4. cd project_folder/app  
5. python main.py
  
Сайт доступен по http://localhost:8000  
  
# Данные тестовых пользователей
email: test@test.ru; password: uHaE!DK  
email: admin@test.ru; password: fVQvB  

# Секретный ключ
m+IOXLQe|Kg)1I2M4(4-]iK%f|0#DN)P9  
  
Route для платежной системы http://localhost:8000/payment  

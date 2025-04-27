# Инструкция по запуску с docker-compose  
1. cd project_folder  
2. docker-compose up  

# Инструкция по запуску без docker-compose
1. python 3.9+
2. pip install sanic sqlalchemy sanic_jinja2 psycopg2

Устанавливаем переменную с ссылкой на созданную пустую базу данных postgreSQL, в которую будем вносить изменения  
(powershell)  
3. $env:DB_URL = "postgresql+psycopg2://user:password@host:port/database.db"  
(bash)  
3. export DB_URL = "postgresql+psycopg2://user:password@host:port/database.db"  
  
4. cd project_folder/app  
5. python main.py  
  
# Данные тестовых пользователей
email: test@test.ru; password: uHaE!DK  
email: admin@test.ru; password: fVQvB  

# Секретный ключ
m+IOXLQe|Kg)1I2M4(4-]iK%f|0#DN)P9

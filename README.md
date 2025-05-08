# Инструкция по запуску с docker-compose  
1. cd project_folder  
2. docker-compose up  
  
Swagger доступен по http://localhost:8000/docs#/  
  
# Инструкция по запуску без docker-compose
1. python 3.12+
2. pip install fastapi sqlalchemy psycopg2 pydantic python-jose passlib[bcrypt]  

(Если не получатеся psycopg2, то попробуйте pip install psycopg2-binary)

Устанавливаем переменную с ссылкой на созданную пустую базу данных postgreSQL, в которую будем вносить изменения  
(powershell)  
3. $env:DB_URL = "postgresql+psycopg2://user:password@localhost:port/database.db"  
(bash)  
3. export DB_URL = "postgresql+psycopg2://user:password@localhost:port/database.db"  
  
Например postgresql+psycopg2://postgres:postgres@localhost:5432/async_app.db  
  
4. cd project_folder/app  
5. python main.py
  
Swagger доступен по http://localhost:8000/docs#/  
  
# Данные тестовых пользователей
email: test@test.ru; password: uHaE!DK  
email: admin@test.ru; password: fVQvB  

# Секретный ключ для кодирования паролей
3Dtk6u1PFRNsKri5cQpn8EdqwGG+66JpUCl7oF0i76P+lvgfx1LVp/a0Jh8TSvzJ  

# Секретный ключ для оплаты
m+IOXLQe|Kg)1I2M4(4-]iK%f|0#DN)P9  

Можно изменить в app_config.py  
  
Route для платежной системы http://localhost:8000/payment  

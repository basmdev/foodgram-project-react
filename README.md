# FOODGRAM
## Социальная сеть для обмена рецептами

### Описание
На этом сайте пользователи могут публиковать свои рецепты, подписываться на других пользователей, добавлять рецепты в избранное, составлять и скачивать список необходимых продуктов для рецепта.

### Технологии
- Python 3.11.4
- Django 4.2.3

### Запуск проекта
Перед запуском проекта, создайте в папке `infra` файл `.env` и заполните его по шаблону `.env.example`.  
  
Чтобы запустить проект, выполните команду:  
```docker compose up --build```  
  
Создайте и примените миграции:  
```docker exec foodgram_backend python manage.py makemigrations```  
```docker exec foodgram_backend python manage.py migrate```  
  
Соберите статику:  
```docker exec foodgram_backend python manage.py collectstatic --noinput```  
  
Загрузите ингредиенты по желанию с помощью команды:  
```docker exec foodgram_backend python manage.py load_data```  

### Автор проекта
Магомет Басханов
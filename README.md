# FOODGRAM
## Социальная сеть для обмена рецептами

### Описание
На этом сайте пользователи могут публиковать свои рецепты, подписываться на других пользователей, добавлять рецепты в избранное, составлять и скачивать список необходимых продуктов для рецепта.

### Технологии
- Python 3.11.4
- Django 4.2.3

### Запуск проекта
Перед запуском проекта, создайте в папке `infra` файл `.env` и заполните его по шаблону `.env.example`.

1. Перейдите в следующую директорию:
```bash
cd infra
```
  
2. Выполните команду:  
```bash
docker compose up --build
```  
  
3. Примените миграции:  
```bash
docker exec foodgram_backend python manage.py migrate
```  
  
4. Соберите статику:  
```bash
docker exec foodgram_backend python manage.py collectstatic --noinput
```  
  
5. Загрузите ингредиенты по желанию с помощью команды:  
```bash
docker exec foodgram_backend python manage.py load_data
```  
  
### Автор проекта

Mohammed Baskhanov (basmdev)
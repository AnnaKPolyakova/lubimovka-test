# lubimovka-test

## Технологии и требования
```
Python 3.9+
Django
Django REST Framework

```

## Установка локально

```
1. Сколонируйте репозиторий проекта
2. Установите рабочее окружение и зависимости
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
3. Теперь можно запустить проект, он будет использовать БД в контейнере:
python manage.py runserver
```

## Создание супер пользователя
```
python manage.py createsuperuser
```

## Документация API доступна по следущим адресам:
```
http://127.0.0.1:8000/api/schema/swagger-ui/
http://127.0.0.1:8000/api/schema/redoc/
```


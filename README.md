<!-- Дополню ридми перед деплоем, что бы информация была актуальна -->
# Cервис Foodgram, "Продуктовый помощник"  

## Описание

Онлайн-сервис Foodgram и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

#### Документация к API доступна по адресу <http://127.0.0.1/api/docs/> после локального запуска проекта

### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX

#### Локальный запуск проекта

- Склонировать репозиторий:

```bash
   git clone https://github.com/sokolov055/foodgram-project-react.git
```

```bash
   cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

Команда для установки виртуального окружения на Mac или Linux:

```bash
   python3 -m venv env
   source env/bin/activate
```

Команда для Windows:

```bash
   python -m venv venv
   source venv/Scripts/activate
```

- Перейти в директорию infra:

```bash
   cd infra
```


- Создать и запустить контейнеры Docker:

```bash
   docker-compose up 
```

Установить зависимости из файла requirements.txt:

```bash
   cd ..
   cd backend
   pip install -r requirements.txt
```

```bash
   python manage.py migrate
```

Заполнить базу тестовыми данными об ингредиентах:

```bash
   python manage.py load_data
```

Создать суперпользователя, если необходимо:

```bash
python manage.py createsuperuser
```

- Запустить локальный сервер:

```bash
   python manage.py runserver
```

### Автор:

Константин Соколов - [https://github.com/sokolov055/]
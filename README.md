# Продуктовый помощник 
#### Foodgram
##### bellyfeast.hopto.org
##### логин evgeniifilchin@gmail.com
##### пароль Sa12345678



## Описание
Ресурс, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий

- Python 
- Django Rest Framework 
- Nginx
- Gunicorn
- PostgreSQL
- Docker
- Docker-compose
- GitHub Actions
- Linux Ubuntu

## Документация
Redoc можно посмореть после локального запуска проекта по адресу:
```
http://localhost:7000/api/docs/
```

## Инструкция
Чтобы развернуть локально проект с помощью Docker, необходимо склонировать репозиторий себе на компьютер:

```bash
git clone <название репозитория>
```

```bash
cd <название репозитория> 
```

Cоздать и активировать виртуальное окружение:

```bash
python -m venv venv
source venv/Scripts/activate
```

Создать файл .env по образцу ".env.example":

```bash
touch .env
```

Установить зависимости из файла requirements.txt:

```bash
cd ../backend
pip install -r requirements.txt
```

Запустите Docker Compose на своём компьютере. 

В папках frontend/, backend/ и  nginx/ соберите образы foodgram_frontend, foodgram_backend и foodgram_gateway.

В директории frontend:

```bash
cd frontend  
docker build -t jfilchin/foodgram_frontend .
```

То же в директории backend:

```bash
cd ../backend  
docker build -t jfilchin/foodgram_backend .
```

И то же и в nginx:

```bash
cd ../nginx    
docker build -t jfilchin/foodgram_gateway .
```

Для сборки название файла конфигурации надо указывать явным образом. Имя файла указывается после ключа -f.

```bash
docker compose -f docker-compose.production.yml up
```
Собрать статику:
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/backend_static/static/
```
Выполнить миграции:
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
Импортировать данные (теги и ингредиенты):
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py import_data
```
Создать супер пользователя:
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
Перейти по ссылке:
```
http://localhost:7000/
```

## Автор
[JFilchin](https://github.com/JFilchin)
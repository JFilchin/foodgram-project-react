# Продуктовый помощник 

## Описание
Ресурс, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий

![Python](https://img.shields.io/badge/-Python-black?style=for-the-badge&logo=Python&logoColor=) 
![Django](https://img.shields.io/badge/-Django-black?style=for-the-badge&logo=Django&logoColor=E9D54D)
![DjangoRESTFramework](https://img.shields.io/badge/-DRF-black?style=for-the-badge&logo=DjangoRESTFramework)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-black?style=for-the-badge&logo=PostgreSQL&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-black?style=for-the-badge&logo=gunicorn&logoColor=43A047)
![Nginx](https://img.shields.io/badge/-Nginx-black?style=for-the-badge&logo=Nginx&logoColor=43A047)
![Docker](https://img.shields.io/badge/-Docker-black?style=for-the-badge&logo=Docker)
![Ubuntu](https://img.shields.io/badge/-Ubuntu-black?style=for-the-badge&logo=Ubuntu)
![GitHubActions](https://img.shields.io/badge/-GitHubActions-black?style=for-the-badge&logo=GitHubActions)

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
# Сервис авторизации 
## python:3.9

## Для запуска в контейнере нужно создать файл .env с переменными
```
PROJECT_NAME=movies_auth
COMPOSE_PROJECT_NAME=movies_auth
DOCKER_REGISTRY_NAME=local
DEBUG=0

## при первом запуске (для создания таблиц в базе)
FIRST_START=1

## postgres
POSTGRES_DB=auth
POSTGRES_PASSWORD=<db pass>
POSTGRES_USER=<db user>

### БД
DATABASE_PASSWORD=<db pass>
DATABASE_USER=<db user>
DATABASE_NAME=auth
DATABASE_HOST=postgres-auth
DATABASE_PORT=5432

## Настройки Redis
REDIS_HOST=redis_auth
REDIS_PORT=6379

JWT_SECRET_KEY=<Top secret key>
```

выполнить `docker-compose up --build`
Swagger будет доступен по адресу [http://0.0.0.0:5000/apidocs/](http://0.0.0.0:5000/apidocs/)

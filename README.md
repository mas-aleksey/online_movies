# Проектная работа: Биллинг


облачная БД для сервисов 
```
Postgres
host: rc1a-7irj22qworosif2n.mdb.yandexcloud.net
port: 6432
user: uesr
password: useruser
db_names: [billing, movies, movies-auth, notify]
```

для локального запуска

1. переименуйте `.env` файлы в дериктории `docker-compose-env`
2. не используйте nginx (он настроен для работы на удаленном сервере)
3. вместо него переименуйте `docker-compose.override.yml.example` -> `docker-compose.override.yml
4. запустите сервисы `docker-compose up -d --build` 


Так же можно проверить работу по ссылке
[https://yandexmovies.online](https://yandexmovies.online)

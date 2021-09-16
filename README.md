# Billing project


Cloud DB for services
```
Postgres
host: rc1a-7irj22qworosif2n.mdb.yandexcloud.net
port: 6432
user: uesr
password: ********
db_names: [billing, movies, movies-auth, notify]
```

For local launch

1. rename to `.env` files in path `docker-compose-env`
2. do not use nginx (it configured for stage)
3. instead of rename `docker-compose.override.yml.example` -> `docker-compose.override.yml
4. run all services `docker-compose up -d --build` 


Also, you could check this link out (unavailable now)
[https://yandexmovies.online](https://yandexmovies.online)

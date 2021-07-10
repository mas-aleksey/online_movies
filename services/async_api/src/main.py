import uvicorn
from api.v1 import film, genre, person
from core import config, utils
from storage.elastic import ElasticStorage
import storage.base as base_storage
from cache import redis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=config.PROJECT_NAME,
    description="Предоставляет информацию о фильмах, жанрах и людях, участвовавших в создании произведения",
    # Адрес документации в красивом интерфейсе
    docs_url='/async/openapi',
    # Адрес документации в формате OpenAPI
    openapi_url='/async/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    """Подключаемся к базам при старте сервера"""
    base_storage.storage = ElasticStorage()
    await base_storage.storage.open_connection()
    await redis.on_startup()


@app.on_event('shutdown')
async def shutdown():
    """Отключаемся от баз при выключении сервера"""
    await base_storage.storage.close_connection()
    await redis.on_shutdown()


# Подключаем роутер к серверу, указав префикс /api/v1/film
# Теги указываем для удобства навигации по документации
app.include_router(film.router, prefix='/async/api/v1', tags=['Фильмы'])
app.include_router(genre.router, prefix='/async/api/v1', tags=['Жанры'])
app.include_router(person.router, prefix='/async/api/v1', tags=['Персоны'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=config.LOGGING,
        log_level=utils.log_converter.get(config.LOG_LEVEL),
    )

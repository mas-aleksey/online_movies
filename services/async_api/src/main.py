import logging
import uvicorn
from api.v1 import film, genre, person
from core import config, utils
from storage.elastic import ElasticStorage
import storage.base as base_storage
from cache import redis
import requests
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

LOGGER = logging.getLogger(__file__)
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
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['GET'], allow_headers=['*'])


@app.middleware('http')
async def check_access_user_role(request: Request, call_next):
    is_superuser = False
    roles = {'free'}
    try:
        token = request.cookies.get('authorization') or request.headers.get("authorization")
        if not token:
            raise ValueError('TOKEN is empty')
        headers = {
            'authorization': token,
            'user-agent': request.headers["user-agent"]
        }
        resp = requests.get(config.AUTH_ENDPOINT, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            is_superuser = data.get('is_super') or False
            user_roles = data.get('roles') or []
            roles.update(user_roles)
            LOGGER.info('good response %s', data)
        else:
            LOGGER.info('bad response %s', resp.text)
    except Exception as exc:
        LOGGER.error(exc)
    request.scope["is_superuser"] = is_superuser
    request.scope["roles"] = list(roles)
    response = await call_next(request)
    return response


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

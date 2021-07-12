import uvicorn
from api.v1 import notify_events
from core import settings, utils
import brokers.base as base_broker
from brokers.rabbit_mq import RabbitMQ

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


app = FastAPI(
    title='Notify API',
    description="API сервиса уведомлений",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    """Подключаемся к брокерам при старте сервера"""
    base_broker.mq = RabbitMQ(settings.DNS['rabbit'])


@app.on_event('shutdown')
async def shutdown():
    """Отключаемся от брокеров при выключении сервера"""

app.include_router(notify_events.router, prefix='/api/v1', tags=['Уведомления'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.HOST,
        port=settings.PORT,
        log_config=settings.LOGGING,
        log_level=utils.log_converter.get(settings.LOG_LEVEL),
    )

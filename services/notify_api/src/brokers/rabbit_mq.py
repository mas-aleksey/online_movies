import asyncio
import json
from typing import List, Dict
from aio_pika import connect_robust, Channel, Exchange, Message, DeliveryMode
from brokers.base import BaseProducer
from core import settings


class RabbitMQ(BaseProducer):
    def __init__(self, dns: Dict[str, str], loop=None):
        self.dns = dns
        self.loop = loop or asyncio.get_event_loop()

    async def _produce(self, messages: List[dict], routing_key: str):

        connection = await connect_robust(**self.dns, loop=self.loop)
        async with connection:
            channel: Channel = await connection.channel(on_return_raises=True)
            exchange: Exchange = await channel.declare_exchange(settings.MQ_EXCHANGE_NOTIFY, durable=True)

            for msg in messages:
                payload = json.dumps(msg, ensure_ascii=False)
                message = Message(
                    body=payload.encode(),
                    delivery_mode=DeliveryMode.PERSISTENT,
                    content_type='application/json'
                )
                await exchange.publish(message, routing_key=routing_key)

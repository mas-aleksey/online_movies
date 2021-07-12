import logging
from functools import lru_cache
from collections import defaultdict
from typing import List
from fastapi import Depends
from brokers.base import BaseProducer, get_mq
from models.messages import EventMessage, NotifyType


class MqProducer:
    def __init__(self, mq: BaseProducer):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mq = mq
        self.response = {'status': 'ok'}

    async def push_event(self, event: EventMessage):
        return await self._push([event])

    async def push_events(self, events: List[EventMessage]):
        return await self._push(events)

    async def _push(self, events: List[EventMessage]):
        routing_map = defaultdict(list)
        for event in events:
            if event.type == NotifyType.scheduled:
                routing_map['slow'].append(event.dict())
            if event.type == NotifyType.immediately:
                routing_map['fast'].append(event.dict())

        try:
            for routing_key, messages in routing_map.items():
                await self.mq.produce(messages, routing_key)
                self.logger.info('Produced %s messages for routing_key: %s', len(messages), routing_key)
        except Exception as exc:
            self.logger.error('Rabbit publish error: %s', exc, exc_info=True)
            return None, 'Something went wrong'

        return self.response, None


@lru_cache()
def get_produce_service(mq: BaseProducer = Depends(get_mq)) -> MqProducer:
    return MqProducer(mq)

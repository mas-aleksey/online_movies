from typing import List


class BaseProducer:

    async def produce(self, messages: List[str], routing_key: str):
        return await self._produce(messages, routing_key)

    async def _produce(self, messages: List[str], routing_key: str):
        raise NotImplementedError


mq = None


def get_mq():
    return mq

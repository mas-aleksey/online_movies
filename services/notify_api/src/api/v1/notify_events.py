from http import HTTPStatus
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from models.messages import EventMessage
from services.mq_producer import MqProducer, get_produce_service

router = APIRouter()


@router.post('/event', summary='Принимает событие нотификации')
async def watch_list(
        event: EventMessage,
        service: MqProducer = Depends(get_produce_service),
) -> Dict:
    result, error = await service.push_event(event)
    if error:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
    return result


@router.post('/events', summary='Принимает список событий нотификации')
async def add_new_wish(
        events: List[EventMessage],
        service: MqProducer = Depends(get_produce_service),
) -> Dict:
    result, error = service.push_events(events)
    if error:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error)
    return result

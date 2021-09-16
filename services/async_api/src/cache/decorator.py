from functools import partial
from typing import Callable, Dict, Tuple
from fastapi import Request, Response
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache
from core.config import CACHE_EXPIRE_TIME_IN_SECONDS


def key_builder(
        func: Callable,
        namespace: str,
        request: Request,
        response: Response,
        args: Tuple,
        kwargs: Dict
) -> str:
    path = request.url.components.path
    query_params = str(request.query_params)
    roles = '::'.join(request.scope["roles"])
    return f'{path}::{query_params}::{roles}'


api_cache = partial(
    cache,
    expire=CACHE_EXPIRE_TIME_IN_SECONDS,
    coder=PickleCoder,
    key_builder=key_builder
)

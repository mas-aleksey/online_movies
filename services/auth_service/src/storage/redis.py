import redis
import json
from src.settings import ACCESS_EXPIRES, REFRESH_EXPIRES, REDIS_DNS

redis_db = redis.Redis(**REDIS_DNS)


def _revoke_token(jti: str, pipeline: redis.client.Pipeline, refresh: bool) -> None:
    expires = REFRESH_EXPIRES if refresh else ACCESS_EXPIRES
    pipeline.setex(jti, expires, 'revoked')


def revoke_token(token_jti: str, refresh: bool = False):
    pair_jti = redis_db.get(token_jti)
    pipeline = redis_db.pipeline()

    if pair_jti and pair_jti != b'revoked':
        _revoke_token(pair_jti, pipeline, refresh=not refresh)

    _revoke_token(token_jti, pipeline, refresh=refresh)
    pipeline.execute()


def save_tokens(user_id: str, access_jti: str, refresh_jti: str, user_agent: str) -> None:
    user_tokens = json.loads(redis_db.get(user_id) or '{}')

    pipeline = redis_db.pipeline()
    old_refresh = user_tokens.get(user_agent)
    if old_refresh:
        revoke_token(old_refresh, refresh=True)

    user_tokens[user_agent] = refresh_jti

    pipeline.setex(user_id, REFRESH_EXPIRES, json.dumps(user_tokens))
    pipeline.setex(access_jti, ACCESS_EXPIRES, refresh_jti)
    pipeline.setex(refresh_jti, REFRESH_EXPIRES, access_jti)
    pipeline.execute()


def delete_user_tokens(user_id: str):
    user_tokens = json.loads(redis_db.get(user_id) or '{}')
    pipeline = redis_db.pipeline()
    for refresh_jti in user_tokens.values():
        revoke_token(refresh_jti, refresh=True)
    pipeline.delete(user_id)
    pipeline.execute()


def revoke_access_tokens(user_id: str) -> int:
    user_tokens = json.loads(redis_db.get(user_id) or '{}')
    pipeline = redis_db.pipeline()
    count = 0

    for refresh_jti in user_tokens.values():
        access_jti = redis_db.get(refresh_jti)
        if access_jti and access_jti != b'revoked':
            _revoke_token(access_jti, pipeline, refresh=False)
            count += 1
    pipeline.execute()
    return count

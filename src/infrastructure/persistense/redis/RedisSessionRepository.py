import json

from src.domain.model.Session import Session
from src.infrastructure.configuration.persistense.RedisConnection0Client import redis_0_client


class RedisSessionRepository:

    def __init__(self):
        self.redis = redis_0_client.get_client()

    async def save(self, tg_user_id: int, session: Session) -> Session:
        json_session = json.dumps(session.to_dict())
        await self.redis.hset("sessions", f"session:{tg_user_id}", json_session)
        return session
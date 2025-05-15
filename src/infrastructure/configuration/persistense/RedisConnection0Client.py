from redis.asyncio import Redis

from src.infrastructure.configuration.properties.RedisProperties import RedisProperties

class RedisConnection0Client:

    def __init__(self):
        self.redis_properties = RedisProperties()
        self.redis: Redis = None
        self.__redis_0_url: str = None

    async def connect(self):
        try:
            self.__redis_0_url = (
                f"redis://{self.redis_properties.get_redis_username()}:"
                f"{self.redis_properties.get_redis_password()}@"
                f"{self.redis_properties.get_redis_host()}:"
                f"{self.redis_properties.get_redis_port()}/"
                f"{self.redis_properties.get_redis_db_0()}"
            )
            self.redis = await Redis.from_url(
                url=self.__redis_0_url,
                encoding="utf-8",
                decode_responses=True
            )
            print(f"Connected to Redis via URL: {(
                f"redis://*username*:"
                f"*password*@"
                f"{self.redis_properties.get_redis_host()}:"
                f"{self.redis_properties.get_redis_port()}/"
                f"{self.redis_properties.get_redis_db_0()}"
            )}")
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        if self.redis:
            await self.redis.aclose()
            print("Redis connection closed")

    def get_client(self):
        if not self.redis:
            raise Exception("Redis client not connected")
        return self.redis

redis_0_client = RedisConnection0Client()
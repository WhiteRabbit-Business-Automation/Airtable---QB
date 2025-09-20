import redis
import uuid

class RedisLock:
    def __init__(self, redis_client, lock_key: str, ttl: int = 300):
        """
        :param redis_client: Client instance for Redis.
        :param lock_key: Unique key for the lock (e.g., 'lock:refresh_token:{realm_id}').
        :param ttl: Time in seconds for the lock to be valid (default is 5 minutes).
        """
        self.redis_client = redis_client
        self.lock_key = lock_key
        self.ttl = ttl
        self.lock_uuid = str(uuid.uuid4())

    def acquire(self):
        """
        Intenta adquirir el lock.
        """
        if self.redis_client.setnx(self.lock_key, self.lock_uuid):
            # Si el lock no existía, lo creamos y le damos un tiempo de vida (TTL)
            self.redis_client.expire(self.lock_key, self.ttl)
            return True
        return False

    def release(self):
        """
        Free the lock if it's held by this instance.
        """
        stored_uuid = self.redis_client.get(self.lock_key)
        if stored_uuid and stored_uuid.decode() == self.lock_uuid:
            self.redis_client.delete(self.lock_key)
            return True
        return False

    def is_locked(self):
        """
        Check if the lock is active.
        """
        return self.redis_client.exists(self.lock_key)

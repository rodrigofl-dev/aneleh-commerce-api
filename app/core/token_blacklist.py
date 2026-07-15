from datetime import datetime, timezone

from app.core.redis_client import redis_client

_KEY_PREFIX = "token_blacklist:"


def blacklist_token(token: str, expires_at: int) -> None:
    """Blacklists `token` until its own expiration.

    `expires_at` is the JWT `exp` claim (unix timestamp, in seconds).
    The Redis key TTL is set to match the token's remaining lifetime, so
    entries expire on their own — no cleanup job needed, and the blacklist
    never grows unbounded.
    """
    ttl = expires_at - int(datetime.now(timezone.utc).timestamp())
    if ttl > 0:
        redis_client.set(f"{_KEY_PREFIX}{token}", "1", ex=ttl)


def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"{_KEY_PREFIX}{token}") == 1

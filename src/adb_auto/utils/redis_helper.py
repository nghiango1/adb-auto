import redis
from adb_auto.config.setting import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_USERNAME,
    REDIS_PASSWORD,
    REDIS_SSL,
    REDIS_SSL_CERTFILE,
    REDIS_SSL_KEYFILE,
    REDIS_SSL_CA_CERTS,
)

if REDIS_HOST.lower() in ["localhost", "127.0.0.1"]:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
    )
elif not REDIS_SSL:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
    )
else:  # REDIS_SSL:True
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        ssl=REDIS_SSL,
        ssl_certfile=REDIS_SSL_CERTFILE,
        ssl_keyfile=REDIS_SSL_KEYFILE,
        ssl_ca_certs=REDIS_SSL_CA_CERTS,
    )


if __name__ == "__main__":
    r.set("foo", "bar")
    r.get("foo")

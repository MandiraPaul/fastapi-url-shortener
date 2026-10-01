
import redis

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True
)


if __name__ == "__main__":

    response = redis_client.ping()

    print("Redis connection successful:", response)

    saved_url = redis_client.get("test:abc123")

    print("Saved URL:", saved_url)

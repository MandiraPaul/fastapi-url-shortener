import json
from fastapi import BackgroundTasks
from analytics import save_click


from redis.exceptions import RedisError
from redis_client import redis_client
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import text

from database import engine


app = FastAPI()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://127.0.0.1:6379/1"
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


class URLRequest(BaseModel):
    url: HttpUrl


BASE62_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(number: int) -> str:
    if number == 0:
        return BASE62_CHARACTERS[0]

    encoded = ""

    while number > 0:
        remainder = number % 62
        encoded = BASE62_CHARACTERS[remainder] + encoded
        number = number // 62

    return encoded


@app.get("/")
def home():
    return {
        "message": "URL Shortener API is running"
    }



@app.post("/shorten")
@limiter.limit("10/minute")
def shorten_url(request: Request, data: URLRequest):


    original_url = str(data.url)

    with engine.begin() as connection:

        result = connection.execute(
            text(
                """
                INSERT INTO urls (original_url)
                VALUES (:original_url)
                RETURNING id
                """
            ),
            {
                "original_url": original_url
            }
        )

        url_id = result.scalar_one()

        short_code = base62_encode(url_id)

        connection.execute(
            text(
                """
                UPDATE urls
                SET short_code = :short_code
                WHERE id = :url_id
                """
            ),
            {
                "short_code": short_code,
                "url_id": url_id
            }
        )

    short_url = f"http://127.0.0.1:8000/{short_code}"

    return {
        "id": url_id,
        "original_url": original_url,
        "short_code": short_code,
        "short_url": short_url
    }




@app.get("/{short_code}")
def redirect_to_original_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks
):

    cache_key = f"url:{short_code}"

    url_id = None
    original_url = None

    # Step 1: Check Redis
    try:
        cached_data = redis_client.get(cache_key)

        if cached_data:
            try:
                data = json.loads(cached_data)

                if isinstance(data, dict):
                    url_id = data.get("id")
                    original_url = data.get("original_url")

            except (json.JSONDecodeError, TypeError):
                pass

    except RedisError:
        print("Redis unavailable. Checking PostgreSQL.")

    # Step 2: Check Cache HIT or MISS
    if url_id is not None and original_url:

        print(f"CACHE HIT: {short_code}")

    else:

        print(f"CACHE MISS: {short_code}")

        with engine.connect() as connection:

            result = connection.execute(
                text(
                    """
                    SELECT id, original_url
                    FROM urls
                    WHERE short_code = :short_code
                    """
                ),
                {"short_code": short_code}
            )

            row = result.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Short URL not found"
            )

        url_id = row.id
        original_url = row.original_url

        # Save both URL ID and original URL in Redis
        try:
            redis_client.setex(
                cache_key,
                300,
                json.dumps({
                    "id": url_id,
                    "original_url": original_url
                })
            )

        except RedisError:
            print("Redis unavailable. Continuing with PostgreSQL.")

    # Step 3: Collect click information
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")

    # Step 4: Schedule analytics in the background
    client_ip = request.client.host if request.client else "unknown"

    dedupe_key = f"click:{short_code}:{client_ip}:{user_agent}"

    should_save_click = True

    try:
        is_new_click = redis_client.set(
            dedupe_key,
            "1",
            nx=True,
            ex=2
        )

        should_save_click = bool(is_new_click)

    except RedisError:
        # Redis বন্ধ থাকলে analytics পুরো বন্ধ করব না
        should_save_click = True


    if should_save_click:
        background_tasks.add_task(
            save_click,
            url_id,
            user_agent,
            referrer
        )

        print(f"NEW CLICK: {short_code}")

    else:
        print(f"DUPLICATE CLICK IGNORED: {short_code}")

        # Step 5: Redirect user
    return RedirectResponse(
        url=original_url,
        status_code=302
    )

@app.get("/analytics/{short_code}")
def get_analytics(short_code: str):

    with engine.connect() as connection:

        url_row = connection.execute(
            text(
                """
                SELECT id, original_url
                FROM urls
                WHERE short_code = :short_code
                """
            ),
            {"short_code": short_code}
        ).mappings().first()

        if url_row is None:
            raise HTTPException(
                status_code=404,
                detail="Short URL not found"
            )

        url_id = url_row["id"]

        total_clicks = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM clicks
                WHERE url_id = :url_id
                """
            ),
            {"url_id": url_id}
        ).scalar_one()

        recent_clicks = connection.execute(
            text(
                """
                SELECT clicked_at, user_agent, referrer, country
                FROM clicks
                WHERE url_id = :url_id
                ORDER BY clicked_at DESC
                LIMIT 10
                """
            ),
            {"url_id": url_id}
        ).mappings().all()

    return {
        "short_code": short_code,
        "original_url": url_row["original_url"],
        "total_clicks": total_clicks,
        "recent_clicks": [
            dict(click) for click in recent_clicks
        ]
    }
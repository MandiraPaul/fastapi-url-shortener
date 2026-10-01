
from sqlalchemy import text
from database import engine


def save_click(
    url_id: int,
    user_agent: str | None,
    referrer: str | None
):

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                INSERT INTO clicks
                (url_id, user_agent, referrer)
                VALUES
                (:url_id, :user_agent, :referrer)
                """
            ),
            {
                "url_id": url_id,
                "user_agent": user_agent,
                "referrer": referrer
            }
        )

    print(f"Click saved successfully for URL ID: {url_id}")

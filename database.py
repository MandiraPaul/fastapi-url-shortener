import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


load_dotenv()


database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)


engine = create_engine(database_url)


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()


if __name__ == "__main__":
    try:
        result = test_database_connection()

        if result == 1:
            print("Database connection successful!")

    except Exception as error:
        print("Database connection failed!")
        print(error)
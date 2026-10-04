# FastAPI URL Shortener & Click Analytics Service

A backend URL shortening service built with FastAPI, PostgreSQL, Redis, and Docker.

The project focuses on backend concepts such as persistent storage, caching, rate limiting, click analytics, duplicate-click protection, automated testing, and containerization.

## Features

- Create shortened URLs using Base62 encoding
- Redirect short URLs to their original destinations
- Persistent URL storage with PostgreSQL
- Redis caching using the Cache-Aside pattern
- Cache HIT/MISS handling
- PostgreSQL fallback when Redis is unavailable
- IP-based rate limiting using SlowAPI
- Click analytics using FastAPI BackgroundTasks
- Track total and recent clicks
- User-Agent and referrer tracking
- Duplicate-click protection using Redis
- Input validation and API error handling
- Automated tests with Pytest
- Dockerized FastAPI application
- Docker Compose setup for FastAPI, PostgreSQL, and Redis
- Persistent PostgreSQL Docker volume
- Interactive API documentation with Swagger UI

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- SlowAPI
- Docker
- Docker Compose
- Pytest
- Uvicorn

## Project Structure

```text
fastapi-url-shortener/
├── tests/
│   └── test_main.py
├── main.py
├── database.py
├── redis_client.py
├── analytics.py
├── init.sql
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
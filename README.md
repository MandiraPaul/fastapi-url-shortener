# FastAPI URL Shortener & Click Analytics Service

A production-deployed backend URL shortening and click analytics service built with FastAPI, PostgreSQL, Redis, Docker, and Railway.

The project demonstrates practical backend concepts including persistent storage, caching, rate limiting, click analytics, duplicate-click protection, reverse-proxy-aware client IP handling, automated testing, and containerization.

## Live Deployment

The API is deployed on Railway and is publicly accessible.

- Swagger UI: https://fastapi-url-shortener-production-a175.up.railway.app/docs
- Base URL: https://fastapi-url-shortener-production-a175.up.railway.app

## Features

- Create shortened URLs
- Redirect short URLs to their original destinations
- Persistent URL storage with PostgreSQL
- Redis caching using the Cache-Aside pattern
- Cache HIT/MISS handling
- PostgreSQL fallback when Redis is unavailable
- IP-based rate limiting using SlowAPI
- Rate limit of 10 requests per minute on the `/shorten` endpoint
- Click analytics using FastAPI BackgroundTasks
- Track total and recent clicks
- User-Agent and referrer tracking
- Duplicate-click protection using Redis
- Real client IP detection behind a reverse proxy
- Input validation and API error handling
- Automated API tests with Pytest
- Dockerized FastAPI application
- Docker Compose setup for FastAPI, PostgreSQL, and Redis
- Persistent PostgreSQL Docker volume
- Interactive API documentation with Swagger UI
- Production deployment on Railway

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- SlowAPI
- Docker
- Docker Compose
- Railway
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
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
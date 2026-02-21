# Oddly Backend — Development Guide

## Стек

- Python 3.12, FastAPI, Tortoise ORM (asyncpg), PostgreSQL 16
- JWT auth (PyJWT + bcrypt), S3 uploads (aioboto3), rate limiting (slowapi)
- Тесты: pytest + pytest-asyncio, линтер: ruff

## Команды

```bash
# Запуск сервера
uvicorn src.main:app --reload

# Тесты (тестовая БД на порту 5433)
pytest

# Линтер
ruff check src/ tests/
ruff format src/ tests/

# Миграции
aerich makemigrations
aerich upgrade
```

## Структура

```
src/
├── main.py              # FastAPI app, middleware, lifespan
├── core/                # config, exceptions, logging, rate_limit
├── clients/s3.py        # S3 upload client
├── db/__init__.py       # Tortoise ORM config + init/close
└── modules/
    ├── __init__.py      # api_router с префиксом /api
    ├── auth/            # register, login, JWT, dependencies
    ├── users/           # профили, soft delete
    ├── offers/          # CRUD объявлений
    ├── reservations/    # бронирования (транзакции)
    ├── feed/            # публичная лента
    └── uploads/         # загрузка фото
```

Каждый модуль: `router.py` → `service.py` → `models.py` + `dto.py` + `exceptions.py`.

## Конвенции кода

- Одинарные кавычки (`'string'`)
- Макс. длина строки: 120
- Ruff правила: E, W, F, I, B, C4, UP, N, S, SIM, RUF
- S101/S106 разрешены в тестах (assert, hardcoded passwords)
- Все модели используют UUID в качестве PK
- Async/await везде — синхронного кода нет
- Pydantic v2 DTO для всех request/response
- Исключения наследуются от `src/core/exceptions.py` (NotFoundError, ConflictError, etc.)

## База данных

- Конфиг: `src/db/__init__.py` → `TORTOISE_ORM`
- Модели: `src/modules/{module}/models.py`
- URL конвертируется: `postgresql://` → `asyncpg://`
- Тестовая БД: `localhost:5433/oddly-test` (docker-compose.test.yml)

## Тесты

- `tests/conftest.py` — фикстуры: `client`, `restaurant_client`, `farmer_client`
- `tests/support/factories.py` — фабрики: `UserFactory`, `OfferFactory`, `ReservationFactory`
- `tests/support/auth.py` — `make_auth_header(user)` для тестовых токенов
- Rate limiter отключён в тестах (`limiter.enabled = False` в conftest)
- Каждый тест получает чистую БД (TRUNCATE CASCADE после каждого теста)

## Роли и доступ

- `RESTAURANT` — создаёт offers, завершает reservations
- `FARMER` — просматривает feed, создаёт/отменяет reservations
- JWT токен в заголовке: `Authorization: Bearer <token>`
- `get_current_user` dependency проверяет токен + статус (DELETED/BLOCKED → 401)

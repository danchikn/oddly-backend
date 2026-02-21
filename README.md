# EcoFeed Backend

Бэкенд платформы для перераспределения органических пищевых отходов между предприятиями общественного питания и фермерскими хозяйствами.

Рестораны публикуют объявления о доступных отходах, фермеры просматривают ленту и бронируют подходящие предложения. Коммуникация происходит напрямую по контактным данным.

## Стек

- **Python 3.12** + **FastAPI**
- **PostgreSQL 16** + **Tortoise ORM** + **Aerich** (миграции)
- **JWT** аутентификация (PyJWT + bcrypt)
- **AWS S3** (aioboto3) — загрузка фото
- **slowapi** — rate limiting
- **Docker** + **Docker Compose**

## Быстрый старт

```bash
# Запуск БД и приложения
docker-compose up -d

# Приложение: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### Локальная разработка (без Docker для приложения)

```bash
# Запуск только БД
docker-compose up -d db

# Установка зависимостей
pip install -e ".[dev]"

# Миграции
aerich upgrade

# Запуск сервера
uvicorn src.main:app --reload

# Тесты (нужна тестовая БД на порту 5433)
docker-compose -f docker-compose.test.yml up -d
pytest
```

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения.

| Переменная | Описание | По умолчанию |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/eco-feed` |
| `JWT_SECRET` | Секрет для подписи токенов | `super-secret-change-me` |
| `JWT_EXPIRE_MINUTES` | Время жизни токена (мин) | `1440` (24ч) |
| `S3_ENDPOINT_URL` | URL S3-совместимого хранилища | — |
| `S3_ACCESS_KEY` | S3 access key | — |
| `S3_SECRET_KEY` | S3 secret key | — |
| `S3_BUCKET` | Имя бакета | — |
| `S3_REGION` | Регион | `us-east-1` |
| `S3_PUBLIC_URL` | Публичный URL бакета | — |

## API Endpoints

Базовый префикс: `/api`

### Auth (`/api/auth`)

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| POST | `/auth/register` | — | Регистрация (3 req/min) |
| POST | `/auth/login` | — | Вход (5 req/min) |
| GET | `/auth/me` | JWT | Текущий пользователь |

### Users (`/api/users`)

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| GET | `/users/{id}` | — | Публичный профиль (имя, роль) |
| PATCH | `/users/me` | JWT | Обновить свой профиль |
| POST | `/users/me/delete` | JWT | Удалить аккаунт (soft delete) |

### Offers (`/api/offers`)

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| POST | `/offers` | JWT | Создать объявление |
| GET | `/offers/my` | JWT | Мои объявления (пагинация, фильтр по статусу) |
| GET | `/offers/{id}` | — | Детали объявления |
| PATCH | `/offers/{id}` | JWT (владелец) | Обновить объявление |
| POST | `/offers/{id}/cancel` | JWT (владелец) | Отменить объявление |

### Feed (`/api/feed`)

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| GET | `/feed` | — | Лента открытых объявлений (пагинация) |

### Reservations (`/api/reservations`)

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| POST | `/reservations` | JWT (фермер) | Забронировать объявление |
| GET | `/reservations/my` | JWT | Мои бронирования (пагинация, фильтр) |
| GET | `/reservations/{id}` | JWT (участник) | Детали бронирования |
| POST | `/reservations/{id}/cancel` | JWT (фермер) | Отменить бронирование |
| POST | `/reservations/{id}/complete` | JWT (владелец оффера) | Завершить бронирование |

### Uploads (`/api/uploads`)

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| POST | `/uploads` | JWT | Загрузка фото (макс. 10 файлов, 5MB, jpeg/png/webp) |

## Структура проекта

```
src/
├── main.py                 # Точка входа FastAPI
├── clients/s3.py           # S3 клиент
├── core/
│   ├── config.py           # Настройки (pydantic-settings)
│   ├── exceptions.py       # Базовые HTTP исключения
│   ├── logging.py          # Конфигурация логов
│   └── rate_limit.py       # Rate limiter (slowapi)
├── db/__init__.py          # Tortoise ORM конфигурация
└── modules/
    ├── auth/               # Регистрация, логин, JWT
    ├── users/              # Профили, soft delete
    ├── offers/             # CRUD объявлений
    ├── reservations/       # Бронирования
    ├── feed/               # Публичная лента
    └── uploads/            # Загрузка фото в S3
```

## Роли

- **RESTAURANT** — создаёт объявления, завершает бронирования
- **FARMER** — просматривает ленту, бронирует объявления

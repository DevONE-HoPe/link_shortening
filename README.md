# link_shortening

Бэкенд сервиса по сокращению ссылок. Принимает длинный URL, возвращает короткий идентификатор, редиректит по нему и считает количество переходов.

## Стек

| Компонент | Технология |
|-----------|------------|
| Фреймворк | FastAPI 0.135 |
| ASGI-сервер | Gunicorn + Uvicorn workers |
| БД | PostgreSQL 14 |
| Connection pooler | PgBouncer |
| ORM | SQLAlchemy 2.0 (async) |
| Миграции | Alembic |
| Валидация | Pydantic v2 |
| Логирование | Loguru |
| Тесты | pytest + unittest |

## API

### `POST /shorten`
Создать короткую ссылку.

**Тело запроса:**
```json
{
  "url": "https://example.com/some/very/long/url"
}
```

**Ответ `201`:**
```json
{
  "short_id": "abc12345",
  "short_url": "http://localhost:8000/abc12345",
  "original_url": "https://example.com/some/very/long/url"
}
```

---

### `GET /{short_id}`
Редирект на оригинальный URL. Увеличивает счётчик переходов.

- `302` — редирект
- `404` — ссылка не найдена

---

### `GET /stats/{short_id}`
Статистика по ссылке.

**Ответ `200`:**
```json
{
  "short_id": "abc12345",
  "original_url": "https://example.com/some/very/long/url",
  "clicks": 42,
  "created_at": "2026-03-20T12:00:00"
}
```

- `404` — ссылка не найдена

---

Интерактивная документация доступна по адресу `http://localhost:{APP_PORT}/docs`.

## Запуск через Docker

```bash
cp .env.example .env
# отредактируй .env при необходимости

docker compose up -d --build
```

Контейнеры:
- `backend` — приложение
- `postgres` — база данных
- `pgbouncer` — пул соединений
- `pgbackup` — автобэкапы БД каждые 30 минут

Миграции применяются автоматически контейнером `migrator` при старте.

## Локальный запуск (без Docker)

**Установить зависимости:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Настроить `.env`:**
```bash
cp .env.example .env
```
В `.env` поменяй `DB_HOST` на `localhost` и укажи реквизиты локальной БД.

**Применить миграции:**
```bash
alembic upgrade head
```

**Запустить:**
```bash
uvicorn app.asgi:app --reload
```

## Тесты

```bash
python -m pytest app/tests/ -v
```

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DB_HOST` | Хост БД (`pgbouncer` в Docker, `localhost` локально) | `pgbouncer` |
| `DB_PORT` | Порт БД | `5432` |
| `DB_USER` | Пользователь БД | `user` |
| `DB_PASS` | Пароль БД | `secret` |
| `DB_NAME` | Имя БД | `postgres` |
| `APP_PORT` | Порт приложения | `8000` |
| `COMPOSE_PROJECT_NAME` | Префикс имён контейнеров | `link_shortening` |
| `DEBUG` | Логирование SQL-запросов | `False` |

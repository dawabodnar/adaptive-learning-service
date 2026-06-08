# ─────────────────────────────────────────────────────────────────────────────
# backend/Dockerfile
# Контейнер для бекенду FastAPI (Python 3.12).
# Розміщення: backend/Dockerfile
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# Робоча директорія всередині контейнера
WORKDIR /app

# Системні залежності для psycopg2-binary, bcrypt, cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Спочатку — лише requirements (краще кешується)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Тепер — код застосунку
COPY app/ app/
COPY scripts/ scripts/

# Порт, на якому слухає Uvicorn
EXPOSE 8000

# Перевірка живості контейнера (для docker compose healthcheck)
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/docs > /dev/null || exit 1

# Запуск ASGI-сервера з uvloop та httptools (вже у requirements.txt)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

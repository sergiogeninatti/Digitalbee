FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-root --without dev

COPY src/ /app/src/
COPY .env /app/.env

CMD ["poetry", "run", "python", "src/app.py"]

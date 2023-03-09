FROM python:3.10

ENV PYTHONPATH /line_provider
ENV POETRY_VIRTUALENVS_CREATE false

RUN apt-get update && apt-get install -qq -y \
    build-essential libpq-dev netcat --no-install-recommends

WORKDIR /line_provider/

RUN pip install --upgrade pip && pip install poetry psycopg2

COPY services/line_provider/poetry.lock services/line_provider/pyproject.toml /line_provider/

RUN poetry install
COPY services/line_provider/ /line_provider/
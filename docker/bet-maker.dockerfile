FROM python:3.10

ENV PYTHONPATH /bet_maker
ENV POETRY_VIRTUALENVS_CREATE false

RUN apt-get update && apt-get install -qq -y build-essential libpq-dev netcat --no-install-recommends

WORKDIR /bet_maker/

RUN pip install --upgrade pip && pip install poetry psycopg2

COPY services/bet_maker/poetry.lock services/bet_maker/pyproject.toml /bet_maker/

RUN poetry install
COPY services/bet_maker/ /bet_maker/
FROM python:3.9-slim

RUN pip install poetry

RUN mkdir /app
COPY poetry.lock /app
COPY pyproject.toml /app

WORKDIR /app

RUN poetry install --no-dev

COPY digital_library /app/digital_library
CMD [ "poetry", "run", "python", "-m", "digital_library" ]

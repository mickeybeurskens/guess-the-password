FROM python:3.11 AS requirements-stage

WORKDIR /tmp
 
RUN pip install poetry
 
COPY ./pyproject.toml ./poetry.lock* /tmp/
 
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev --with webapp

FROM python:3.11

WORKDIR /app
 
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
 
COPY ./config /config

COPY ./game /game

COPY ./frontend /frontend

COPY ./cli.py /cli.py

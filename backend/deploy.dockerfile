FROM python:3.11-buster

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src/ ./src
COPY scripts/ ./scripts

RUN cp ./src/alembic.ini.example ./src/alembic.ini

EXPOSE 5000
CMD ["/bin/sh", "./scripts/entry.sh"]
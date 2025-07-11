FROM python:3.12-bookworm

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

RUN apt update && apt install -y cron

RUN mkdir scripts

COPY requirements.txt .
COPY pyproject.toml .
COPY alembic.ini.example alembic.ini
COPY scripts/entry.sh scripts/entry.sh
COPY scripts/cron /etc/cron.d/appointment-cron

# Setup cron permissions
RUN chmod 0644 /etc/cron.d/appointment-cron
RUN crontab /etc/cron.d/appointment-cron

COPY src .

RUN pip install --upgrade pip
RUN pip install .'[deploy]'

ARG RELEASE_VERSION
ENV RELEASE_VERSION=$RELEASE_VERSION

EXPOSE 5000
CMD ["/bin/bash", "./scripts/entry.sh"]

FROM python:3.11-bookworm

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

RUN apt update && apt install -y cron

RUN mkdir scripts

COPY requirements.txt .
COPY pyproject.toml .
COPY alembic.ini.example alembic.ini
COPY scripts/dev-entry.sh scripts/dev-entry.sh
COPY scripts/cron /etc/cron.d/appointment-cron

# Setup cron permissions
RUN chmod 0644 /etc/cron.d/appointment-cron
RUN crontab /etc/cron.d/appointment-cron

# Dev only
RUN echo '!! If the next step fails, copy .env.example to .env in the backend folder !!'
COPY .env .

RUN pip install --upgrade pip
RUN pip install .'[deploy]'

# Install our code
COPY src/appointment /app/appointment

EXPOSE 5000
CMD ["/bin/sh", "./scripts/dev-entry.sh"]

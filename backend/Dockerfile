FROM python:3.12-bookworm

# Unprivileged runtime user. Numeric so Kubernetes `runAsNonRoot` can verify it.
ARG APP_UID=10001
RUN groupadd --system --gid ${APP_UID} app \
    && useradd --system --uid ${APP_UID} --gid app --no-create-home --home-dir /app app

RUN mkdir app
WORKDIR /app

ENV PYTHONPATH=.
# Log to stdout, not a file in the (read-only to the app user) working directory.
ENV LOG_USE_STREAM=1

RUN mkdir scripts

COPY requirements.txt .
COPY pyproject.toml .
COPY alembic.ini.example alembic.ini
COPY scripts/entry.sh scripts/entry.sh
COPY scripts/uvicorn_log_config.json scripts/uvicorn_log_config.json

COPY src .

RUN pip install .'[deploy]'

# Application code stays root-owned (read-only to the app user). Only the
# download-legal / generate-docs output directory is writable.
RUN mkdir -p appointment/tmp && chown app:app appointment/tmp

ARG RELEASE_VERSION
ENV RELEASE_VERSION=$RELEASE_VERSION

USER ${APP_UID}:${APP_UID}

EXPOSE 5000
CMD ["/bin/bash", "./scripts/entry.sh"]

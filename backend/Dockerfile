FROM python:3.12-bookworm

# uv installs dependencies from uv.lock (hash-verified, exact versions).
COPY --from=ghcr.io/astral-sh/uv:0.13.0@sha256:cdc6093146eb3ff6a40107b38f008b789e050e77ad87865e381d9917da55a168 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

RUN apt update && apt install -y cron

RUN mkdir scripts

COPY requirements.txt .
COPY pyproject.toml .
COPY uv.lock .
COPY alembic.ini.example alembic.ini
COPY scripts/entry.sh scripts/entry.sh
COPY scripts/uvicorn_log_config.json scripts/uvicorn_log_config.json
COPY scripts/cron /etc/cron.d/appointment-cron

# Setup cron permissions
RUN chmod 0644 /etc/cron.d/appointment-cron
RUN crontab /etc/cron.d/appointment-cron

# Fail the build if uv.lock is out of date with pyproject.toml/requirements.txt.
RUN uv lock --check

# Third-party dependencies first (cached layer), exactly as locked and
# hash-verified. Wheels only, so no dependency build scripts run.
RUN uv sync --frozen --no-dev --extra cli --extra db --no-install-project --no-build

COPY src .

# Then the appointment package itself: our own code, the only build step.
RUN uv sync --frozen --no-dev --extra cli --extra db --no-editable

ARG RELEASE_VERSION
ENV RELEASE_VERSION=$RELEASE_VERSION

EXPOSE 5000
CMD ["/bin/bash", "./scripts/entry.sh"]

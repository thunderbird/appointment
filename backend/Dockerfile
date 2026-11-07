# Export uv.lock as a hashed requirements file, with a pinned uv. Only the
# exported file is copied into the runtime image.
FROM ghcr.io/astral-sh/uv:0.11.21-alpine AS requirements
WORKDIR /src
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --extra deploy --group build --no-emit-project \
    --output-file requirements.lock

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

# Third-party dependencies exactly as pinned in uv.lock: hash-verified wheels
# only, so no package setup scripts run. The `build` group adds setuptools for
# the app install below.
COPY --from=requirements /src/requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir --require-hashes --only-binary :all: --no-deps -r /tmp/requirements.lock \
    && rm /tmp/requirements.lock

COPY src .

# The app itself (for the `run-command` entry point), built offline against the
# dependencies installed above.
RUN pip install --no-cache-dir --no-deps --no-index --no-build-isolation .

# Application code stays root-owned (read-only to the app user). Only the
# download-legal / generate-docs output directory is writable.
RUN mkdir -p appointment/tmp && chown app:app appointment/tmp

ARG RELEASE_VERSION
ENV RELEASE_VERSION=$RELEASE_VERSION

USER ${APP_UID}:${APP_UID}

EXPOSE 5000
CMD ["/bin/bash", "./scripts/entry.sh"]

#!/bin/bash

# Usage:
#   CONTAINER_ROLE selects the process this container runs:
#     api     - Backend API server (default)
#     worker  - Celery worker
#     beat    - Celery beat scheduler. Run exactly one instance.
#     flower  - Celery Flower monitoring UI
#   SKIP_DB_MIGRATIONS=true makes the api role skip `update-db` on boot.

echo "Entry script starting..."

CONTAINER_ROLE="${CONTAINER_ROLE:-api}"
CELERY_APP="appointment.celery_app:celery"

case "$CONTAINER_ROLE" in
    api)
        if [[ "$IS_LOCAL_DEV" == "yes" ]]; then
            echo "Running setup"
            run-command main setup
        fi

        if [[ "${SKIP_DB_MIGRATIONS,,}" == "true" ]]; then
            echo "Skipping update-db (SKIP_DB_MIGRATIONS is set)"
        else
            echo "Running update-db"
            run-command main update-db
        fi

        if [[ "$IS_LOCAL_DEV" == "yes" ]]; then
            echo "Starting cron service"
            service cron start
        fi

        ARGS=(--factory appointment.main:server --host 0.0.0.0 --port 5000 --log-config scripts/uvicorn_log_config.json)

        if [[ "$IS_LOCAL_DEV" == "yes" ]]; then
            ARGS+=(--reload --log-level info)
        fi

        echo "Running uvicorn with these arguments: '${ARGS[*]}'"
        exec uvicorn "${ARGS[@]}"
        ;;
    worker)
        echo "Starting Celery worker..."
        exec celery -A "$CELERY_APP" worker -l INFO -Q appointment
        ;;
    beat)
        echo "Starting Celery beat..."
        exec celery -A "$CELERY_APP" beat -l INFO
        ;;
    flower)
        echo "Starting Celery Flower..."
        exec celery -A "$CELERY_APP" flower -l INFO
        ;;
    *)
        echo "Unrecognized CONTAINER_ROLE: $CONTAINER_ROLE"
        exit 1
        ;;
esac

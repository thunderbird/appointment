#!/bin/bash

# Usage:
#   CONTAINER_ROLE selects the process this container runs: api (default), worker, beat, flower.
#   SKIP_DB_MIGRATIONS=true makes the api role skip `update-db` on boot.
#   CELERY_EMBED_BEAT=false makes the worker role run without embedded beat.

echo "Entry script starting..."

CONTAINER_ROLE="${CONTAINER_ROLE:-api}"
echo "CONTAINER_ROLE=$CONTAINER_ROLE"
CELERY_APP="appointment.celery_app:celery"

case "$CONTAINER_ROLE" in
    api)
        if [[ "$IS_LOCAL_DEV" == "yes" ]]; then
            echo "Running setup"
            run-command main setup
        fi

        if [[ "${SKIP_DB_MIGRATIONS,,}" == "true" ]]; then
            echo "Skipping update-db (SKIP_DB_MIGRATIONS=$SKIP_DB_MIGRATIONS)"
        else
            echo "Running update-db"
            run-command main update-db || { echo "update-db failed" >&2; exit 1; }
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
        WORKER_ARGS=(-A "$CELERY_APP" worker -l INFO)
        # Embedded beat stays on by default so legacy ECS, which has no beat
        # task, keeps running the schedule. Kubernetes sets this false and runs
        # the dedicated beat role instead.
        if [[ "${CELERY_EMBED_BEAT,,}" != "false" ]]; then
            WORKER_ARGS+=(--beat)
        fi
        WORKER_ARGS+=(-Q appointment)
        exec celery "${WORKER_ARGS[@]}"
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
        echo "Unrecognized CONTAINER_ROLE: $CONTAINER_ROLE" >&2
        exit 1
        ;;
esac

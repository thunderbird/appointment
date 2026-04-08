#!/bin/bash

# Usage:
#   Set CONTAINER_ROLE to control which process this container runs:
#     worker  — Celery worker
#     beat    — Celery beat scheduler
#     (unset) — Backend API server (default)

echo "Entry script starting..."

if [[ "$CONTAINER_ROLE" == "worker" ]]; then
    echo "Starting Celery worker..."
    celery -A appointment.celery_app:celery worker -l INFO -Q appointment
elif [[ "$CONTAINER_ROLE" == "beat" ]]; then
    echo "Starting Celery beat scheduler..."
    celery -A appointment.celery_app:celery beat -l INFO
elif [[ "$CONTAINER_ROLE" == "flower" ]]; then
    echo "Starting Flower monitoring..."
    celery -A appointment.celery_app:celery flower --port=5555
else
    if [[ "$IS_LOCAL_DEV" == "yes" ]]; then
        echo "Running setup"
        run-command main setup
    fi
    echo "Running update-db"
    run-command main update-db

    if [[ "$IS_LOCAL_DEV" == "yes" ]]; then
        echo "Starting cron service"
        service cron start
    fi

    ARGS="--factory appointment.main:server --host 0.0.0.0 --port 5000"

    if [[ "$IS_LOCAL_DEV" == "yes" ]]; then
        ARGS="$ARGS --reload --log-level trace"
    fi

    echo "Running uvicorn with these arguments: '$ARGS'"
    uvicorn $ARGS
fi

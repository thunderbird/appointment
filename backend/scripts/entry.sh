#!/bin/bash

echo "Entry script starting..."

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
    ARGS="$ARGS --reload"
fi

echo "Running uvicorn with these arguments: '$ARGS'"
uvicorn $ARGS

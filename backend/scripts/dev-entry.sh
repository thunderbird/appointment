#!/bin/sh

run-command main setup
run-command main update-db

# Start cron
service cron start

# Start up real webserver
uvicorn --factory appointment.main:server --reload --host 0.0.0.0 --port 5173


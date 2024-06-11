#!/bin/sh

run-command main setup
run-command main update-db

# Start up fake mail server
python -u -m smtpd -n -c DebuggingServer localhost:8050 &

# Start cron
service cron start

# Start up real webserver
uvicorn --factory appointment.main:server --reload --host 0.0.0.0 --port 5173


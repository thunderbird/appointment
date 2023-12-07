#!/bin/sh

run-command update-db

# Start up fake mail server
python -u -m smtpd -n -c DebuggingServer localhost:8050 &

# Start up real webserver
uvicorn --factory src.appointment.main:server --reload --host 0.0.0.0 --port 5173

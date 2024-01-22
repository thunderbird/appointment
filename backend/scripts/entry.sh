#!/bin/sh

run-command main update-db

uvicorn --factory appointment.main:server --host 0.0.0.0 --port 5000

#!/bin/sh

run-command update-db

uvicorn --factory appointment.main:server --host 0.0.0.0 --port 5000

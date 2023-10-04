#!/bin/sh

run-command update-db

uvicorn --factory src.appointment.main:server --host 0.0.0.0 --port 5000
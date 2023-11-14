#!/bin/sh

run-command update-db

uvicorn --factory src.appointment.main:server --reload --host 0.0.0.0 --port 8090
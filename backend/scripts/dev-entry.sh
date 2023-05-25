#!/bin/sh

cd src
echo 'Starting migrations...'
alembic current
alembic upgrade head
echo 'Finished migrations!'
cd ../

uvicorn src.main:app --reload --host 0.0.0.0 --port 8090
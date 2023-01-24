FROM python:3.11-buster

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src/ .
CMD touch /app/src/appointment.db
CMD mv /app/src/appointment.ini.example /app/src/appointment.ini

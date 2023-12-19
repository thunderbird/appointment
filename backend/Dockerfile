FROM python:3.11-buster

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

RUN mkdir scripts

COPY requirements.txt .
COPY pyproject.toml .
COPY alembic.ini.example alembic.ini
COPY scripts/dev-entry.sh scripts/dev-entry.sh

# Dev only
COPY .env .

RUN pip install --upgrade pip
RUN pip install .'[deploy]'

# Add this hack to line it up with our dev environment.
# I'll buy whoever fixes this a coffee.
RUN mkdir src
RUN ln -s /app/appointment src/appointment

EXPOSE 5000
CMD ["/bin/sh", "./scripts/dev-entry.sh"]

FROM python:3.11-bookworm

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

RUN apt update && apt install -y cron

RUN mkdir scripts

COPY requirements.txt .
COPY pyproject.toml .
COPY alembic.ini.example alembic.ini
COPY scripts/entry.sh scripts/entry.sh
COPY scripts/cron /etc/cron.d/appointment-cron

# Setup cron permissions
RUN chmod 0644 /etc/cron.d/appointment-cron
RUN crontab /etc/cron.d/appointment-cron

# Needed for deploy, we don't have a volume attached
COPY src .

# Remove setup.py as we don't need it on stage/prod
RUN rm /app/appointment/commands/setup.py
COPY scripts/dummy_setup.py /app/appointment/commands/setup.py

RUN pip install --upgrade pip
RUN pip install .'[deploy]'

# install removes the src file and installs the application as /app/appointment
# that's fine, but uhh let's add this hack to line it up with our dev environment.
# I'll buy whoever fixes this a coffee.
RUN mkdir src
RUN ln -s /app/appointment src/appointment

ARG RELEASE_VERSION
ENV RELEASE_VERSION=$RELEASE_VERSION

EXPOSE 5000
CMD ["/bin/sh", "./scripts/entry.sh"]

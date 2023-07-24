# Thunderbird Appointment

Invite others to grab times on your calendar. Choose a date. Make appointments as easy as it gets.

## Get started

### With Docker

```bash
git clone https://github.com/thundernest/appointment
cd appointment
docker-compose up -d --build
```

A Mysql database will be accessible via `localhost:3306` with username and password set to: `tba`

### Manual Setup

Make sure to have the following prerequisites available:

```plain
Python >= 3.10
Node.js >= 16.0
```

Run application for development with hot reloading backend and frontend:

1. Get the application data

    ```bash
    git clone https://github.com/thundernest/appointment
    ```

2. Install, configure and run python backend (it's recommended to do this in a virtual environment)

    ```bash
    cd appointment
    pip install -r backend/requirements.txt
    touch backend/src/appointment.db # when using sqlite
    cp backend/.env.example backend/.env # add your own configuration here
    uvicorn backend.src.main:app --reload --port 5000
    ```

    You can now access the backend at [localhost:5000](http://localhost:5000).

3. Install and run vue frontend in a second bash

    ```bash
    cd frontend
    yarn install
    yarn serve
    ```

    You can now access the frontend at [localhost:8080](http://localhost:8080).

4. (optional) Run database migrations

    ```bash
    cd backend/src
    cp alembic.ini.example alembic.ini # add your own configuration here
    alembic init migrations # init migrations once
    alembic current # check database state
    alembic upgrade head # migrate to latest state
    alembic revision -m "create ... table" # create a new migration
    ```

## Testing

To run tests, first install Pytest

```bash
pip install pytest httpx
```

Create an Auth0 test user and add the credentials of that user to `AUTH0_TEST_USER` and `AUTH0_TEST_PASS` in your `.env`. Then `cd` into the project root und simply run

```bash
pytest
```

Note: Since tests include endpoints that trigger mail sending, there must be a running smtp server on your testing system. You can simply run the Python built in server (according to your environment configuration):

```bash
python -m smtpd -n -c DebuggingServer localhost:25
```

## Contributing

Contributions are very welcome. Please lint/format code before creating PRs.

### Backend

Backend is formatted using Ruff and Black.

```bash
pip install ruff
pip install black
```

Commands (from git root)

```bash
ruff backend
black backend
```

### Frontend

Frontend is formatted using ESlint with airbnb rules.

Commands (from /frontend)

```bash
yarn run lint
yarn run lint --fix
```

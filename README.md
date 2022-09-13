# Thunderbird Appointment

Invite others to grab times on your calendar. Choose a date. Make appointments as easy as it gets.

## Get started for development

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
    mv backend/src/appointment.ini.example backend/src/appointment.ini
    uvicorn backend.src.main:app --reload --port 5000
    ```

    You can now access the frontend at [localhost:8080](http://localhost:8080).

3. Install and run vue frontend in a second bash

    ```bash
    cd frontend
    yarn install
    yarn serve
    ```

    You can now access the backend at [localhost:5000](http://localhost:5000).

4. (optional) Run database migrations

    ```bash
    alembic current       # check database state
    alembic upgrade head  # migrate to lates state
    ```

## Testing

To run tests, first install Pytest

```bash
pip install pytest
```

Then `cd` into the project root und simply run

```bash
pytest
```

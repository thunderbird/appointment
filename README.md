# Thunderbird Appointment

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

2. Install and run python backend

    ```bash
    cd appointment
    pip install -r backend/requirements.txt
    uvicorn backend.src.main:app --reload --port 5000
    ```

3. Install and run vue frontend in a second bash

    ```bash
    cd frontend
    yarn install
    yarn serve
    ```

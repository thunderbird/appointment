# Thunderbird Appointment Backend

This is the backend component of Thunderbird Appointment written in Python using FastAPI, SQLAlchemy, and pytest.

## Installation / Running

### Self-hosting

More information will be provided in the future. There is currently a docker file provided which we use to deploy to AWS' ECS which should help you get started.

In order to create a user with password authentication mode, you will need to set `APP_ALLOW_FIRST_TIME_REGISTER=True` in your `.env`.

After the first login you'll want to fill the `APP_ADMIN_ALLOW_LIST` env variable with your account's email to access the basic admin panel located at `/admin/subscribers`.

### Configuration

The backend project uses dotenv files to inject environment variables into the application. A starting template can be found as [.env.example](.env.example). Copy that as your `.env` to get started.

On first run (via [dev-entry.sh](scripts/dev-entry.sh)) a setup command will run filling in some secret environment variables, and the database will initialize.

After that Appointment should be fully usable, however you may want to setup some third-party integrations like Google Calendar connections, or the creation of Zoom meetings. These are clearly labelled in the `.env` file, simply setup accounts for them with the vendor, and enter your values in the `.env` file.

### Linting

Backend is formatted using Ruff.

```bash
pip install ruff
```

Commands

```bash
ruff check
```

### Authentication

This project is deployed with Mozilla Accounts (known as fxa in the code.) Since Mozilla Accounts is for internal use you will need to use password authentication. Note: password authentication does not currently have a registration flow.

### Testing

To run tests in the backend, simply install the package in editing mode:

```bash
cd backend && pip install -e .'[test]'
```

After this you can run all of the tests with:

```bash
cd backend && python -m pytest
```

To run a subset of the test only, provide the test path, for example:

```bash
cd backend && python -m pytest test/integration/
```

And to run a single tests only, for example:

```bash
cd backend && python -m pytest test/integration/test_schedule.py
```

To run the tests with the pytest warnings turned off:

```bash
cd backend && python -m pytest --disable-warnings
```

If you are debugging tests and have print statements inside them, run with this option so the output appears:

```bash
cd backend && python -m pytest -s
```

## Code Coverage

We are using the python `coverage` package to generate code coverage (ie. calculate how much of the source code is exercised during test execution). We are using line (statement) code covearge analysis.

To run the tests with code coverage enabled you simply invoke `coverage run` and then the `pytest` command as normal. For example to run all of the unit and integration tests with code coverage enabled you would run:

```bash
cd backend && coverage run -m pytest --disable-warnings
```

Then after the tests finish you generate the code coverage console report (still in `/backend`):

```bash
coverage report
```

When running locally and looking into code coverage further you may wish to generate an HTML report (still in `/backend`):

```bash
coverage html
```

Then open the resulting `backend/htmlcov/index.html` file in your browser and you can click down into individual source files to see which statements were (and were not) executed during the test session.

Note that the code coverage report will contain the coverage generated for all the tests that were ran in your pytest session; so if you want to measure the code coverage for a subset of tests just provide the test path on the `coverage run -m pytest` command as you normally would, then generate the coverage report(s).

## Database Migrations

To generate a database migration, bash into a running backend container and run:

```bash
alembic revision -m "create ... table"
```

To roll back one migration, run:

```bash
alembic downgrade -1
```

## Commands

Backend has a light selection of cli commands available to be run inside a container.

```bash
run-command main --help
```

```plain
 Usage: run-command main [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                    │
╰────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────╮
│ download-legal                                                 │
│ update-db                                                      │
│ create-invite-codes                                            │
│ setup                                                          │
╰────────────────────────────────────────────────────────────────╯
```

* `download-legal` is an internal command to process privacy policy and terms of service files that will be served by the frontend.
* `update-db` runs on docker container entry, and ensures the latest db migration has run, or if it's a new db then to kickstart that.
* `create-invite-codes n` is an internal command to create invite codes which can be used for user registrations. The `n` argument is an integer that specifies the amount of codes to be generated.
* `setup` a first run setup that fills in some missing environment variables.

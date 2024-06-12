# Thunderbird Appointment Backend

This is the backend component of Thunderbird Appointment written in Python using FastAPI, SQLAlchemy, and pytest.

## Installation / Running

### Self-hosting

More information will be provided in the future. There is currently a docker file provided which we use to deploy to AWS' ECS which should help you get started.

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
cd backend && pip install -e .
```

After this you can run tests with:

```bash
cd backend && python -m pytest
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

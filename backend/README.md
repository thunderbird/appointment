# Thunderbird Appointment Backend

This is the backend component of Thunderbird Appointment written in Python using FastAPI, SQLAlchemy, and pytest. 

## Installation / Running

### Development

A docker file with instructions is provided for development use, please check [appointment/readme.md](../README.md) for more information.

### Self-hosting

More information will be provided in the future. There is currently a docker file provided which we use to deploy to AWS' ECS which should help you get started.

## Configuration

The backend project uses dotenv files to inject environment variables into the application. A starting template can be found as [.env.example](.env.example). Copy that as your .env to get started.

You will want to ensure any variable ending with `_SECRET` has a secret value assigned. Additionally there are values such as SMTP settings for mail, google authentication credentials for google oauth flow with the google calendar api, and zoom api credentials available.

### Authentication

This project is deployed with Mozilla Accounts (known as fxa in the code.) Since Mozilla Accounts is for internal use you will need to use password authentication. Note: password authentication does not currently have a registration flow. 

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
╰────────────────────────────────────────────────────────────────╯
```

* `download-legal` is an internal command to process privacy policy and terms of service files that will be served by the frontend.
* `update-db` runs on docker container entry, and ensures the latest db migration has run, or if it's a new db then to kickstart that.
* `create-invite-codes --n 50` is an internal command to create invite codes which can be used for registrations. The `--n` argument specifies the amount of codes generated, defaults to 50 if left empty.

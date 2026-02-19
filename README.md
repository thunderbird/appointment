# Thunderbird Appointment

> [!IMPORTANT]  
> Thunderbird Appointment is in a beta state, so be prepared to encounter bugs

Invite others to grab times on your calendar. Choose a date. Make appointments as easy as it gets.

## Feedback and Support

If you'd like to give feedback or need support, please see our [Topicbox](https://thunderbird.topicbox.com/groups/services).

## Get started

You can either build preconfigured docker containers (database, backend and frontend) or manually set up the application. A more detailed documentation can be found in the [docs folder](./docs/README.md).

### With Docker

Using Docker is the recommended and for now the only supported method of developing Thunderbird Appointment.

Get the application files and create your `.env` files from the examples:

```bash
git clone https://github.com/thunderbird/appointment
cp appointment/backend/.env.example appointment/backend/.env
cp appointment/frontend/.env.example appointment/frontend/.env
cd appointment
```

Now we can build and run the service in docker:

```bash
docker-compose up -d --build
```

### Authentication

Appointment comes with a simple password-based authentication. This is mostly meant for developing and testing Appointment, but can also be used when self-hosting the app.

For Thunderbird Services, we use our own OIDC provider [Thunderbird Accounts](https://github.com/thunderbird/thunderbird-accounts). If you're starting fresh with Thunderbird Accounts, please review [the documentations](https://github.com/thunderbird/thunderbird-accounts?tab=readme-ov-file#before-you-begin) setting it up. The following steps show a short version of making it work with Appointment.

Get the project files (or symlink to them if you already have a local copy):

```bash
git clone https://github.com/thunderbird/thunderbird-accounts.git accounts
```

Now create a Client:

```bash
# TODO
docker-compose exec accounts uv run manage.py create_client 'Appointment' 'dev contact' 'noreply@example.org' 'https://example.org' --env_type dev --env_redirect_url 'http://localhost:5000/auth/accounts/callback' --env_allowed_hostnames 'localhost:8080,accounts:8087'
```

You should see your Client ID and Client Secret within the output (just example values):

```log
Your client was successfully created with the uuid of f71cf674-228c-4558-b8b2-7780d6a36925
Your Client Details:
* Client ID: f71cf674-228c-4558-b8b2-7780d6a36925
* Client Secret: a5303c654c839d4c8ae8aae7d3b866f581e75280d7f477ee43dcf2200939c6a12ea97fbceda916c50e1136e1615f6e4e523e7a23e2282092b0f88d91c3898b91
```

Copy the Client ID and Client Secret values to your backend's .env file as `TB_ACCOUNTS_CLIENT_ID` and `TB_ACCOUNTS_SECRET` respectively.

---

* Frontend can be accessed via: <http://localhost:8080>
* Backend can be accessed via: <http://localhost:5000>
* OpenAPI docs can be accessed via: <http://localhost:5000/docs> or <http://localhost:5000/redoc>

A PostgreSQL database will be accessible via `localhost:5433` with username and password set to: `tba`: `abcd%efgh`

On first-run the database will initialize, and a first time setup command will be triggered. Going forward database migrations will automatically run on `docker-compose up`.

## Contributing

Contributions are very welcome. Please lint/format code before creating PRs.

Check out the project's respective readmes:

* [Backend Readme](backend/README.md)
* [Frontend Readme](frontend/README.md)
* [E2E Tests Readme](test/e2e/README.md)

### Localization

This project uses [Fluent](https://projectfluent.org/) for localization. Files are located in their respective `l10n/<locale>/*.ftl`.

### Self-hosting

More information is coming soon! If you're adventurous follow the setup steps in each project. Once the project is running the first login will create a new user, any login attempts with new emails after that will check against existing credentials.

### Deployment

When changes are merged to main, a new [release](https://github.com/thunderbird/appointment/releases/) is cut, and the changes are deployed to [stage.appointment.day](https://stage.appointment.day/).

After you've checked staging and it's ready to push to production, edit the release entry, and press the 'Publish release' button.

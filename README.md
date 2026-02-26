# Thunderbird Appointment

> [!IMPORTANT]  
> Thunderbird Appointment is in a beta state, so be prepared to encounter bugs

Invite others to grab times on your calendar. Choose a date. Make appointments as easy as it gets.

## Feedback and Support

If you'd like to give feedback or need support, please see our [Topicbox](https://thunderbird.topicbox.com/groups/services).

## Get started

Using Docker is the recommended and for now the only supported method of building and developing Thunderbird Appointment. A detailed technical documentation of the application architecture can be found in the [docs folder](./docs/README.md) (still work-in-progress).

### Installation

Get the application files and create your `.env` files from the examples:

```bash
git clone https://github.com/thunderbird/appointment
cp appointment/backend/.env.example appointment/backend/.env
cp appointment/frontend/.env.example appointment/frontend/.env
cd appointment
```

Make sure, that the `backend/.env` file contains `APP_ALLOW_FIRST_TIME_REGISTER=True` and that you added your account's email address to the `APP_ADMIN_ALLOW_LIST` env variable. This will enable the creation of your first admin user.

Build and run the service in docker:

```bash
docker-compose up -d --build
```

This will create and start 5 different containers (backend, frontend, postgres, redis and mailpit).

* Frontend can be accessed via: <http://localhost:8080>
* Backend can be accessed via: <http://localhost:5000>
* The PostgreSQL database will be accessible via `localhost:5433` with username: password set to `tba`: `abcd%efgh`
* OpenAPI docs can be accessed via: <http://localhost:5000/docs> or <http://localhost:5000/redoc>
* Mailpit docs can be accessed via: <http://localhost:8025>

On first-run the database will initialize, and a first time setup command will be triggered. Going forward database migrations will automatically run on `docker-compose up`.

### Authentication

Appointment includes simple password-based authentication. This is meant for developing and testing Appointment, but can also be used when self-hosting the app.

When you access the frontend the first time, you will see a first-time-user login form. Enter the email address you configured in your allow list and a password. This login will create the first user (also called 'subscriber' in Appointment) granting you access to the application. Any login attempts with other email addresses after that will check against existing credentials.

> [!NOTE]
> For Thunderbird Services, we use our own OIDC provider [Thunderbird Accounts](https://github.com/thunderbird/thunderbird-accounts). If you're starting fresh with Thunderbird Accounts, please review [the documentations](https://github.com/thunderbird/thunderbird-accounts?tab=readme-ov-file#before-you-begin) setting it up.

## Contributing

Contributions are very welcome. Please lint/format code before creating PRs.

Check out the project's respective readmes:

* [Backend Readme](backend/README.md)
* [Frontend Readme](frontend/README.md)
* [E2E Tests Readme](test/e2e/README.md)

### Localization

This project uses [Fluent](https://projectfluent.org/) for localization. Files are located in their respective `l10n/<locale>/*.ftl`.

### Deployment

When changes are merged to main, a new [release](https://github.com/thunderbird/appointment/releases/) is cut, and the changes are deployed to [stage.appointment.day](https://stage.appointment.day/).

After you've checked staging and it's ready to push to production, edit the release entry, and press the 'Publish release' button.

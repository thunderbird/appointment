# Thunderbird Appointment

> [!IMPORTANT]  
> Thunderbird Appointment is in a beta state, so be prepared to encounter bugs

Invite others to grab times on your calendar. Choose a date. Make appointments as easy as it gets.

## Feedback and Support

If you'd like to give feedback or need support, please see our [Topicbox](https://thunderbird.topicbox.com/groups/services).

## Get started

You can either build preconfigured docker containers (database, backend and frontend) or manually set up the application. A more detailed documentation can be found in the [docs folder](./docs/README.md).

### With Docker

This is the recommended and only supported method of developing Thunderbird Appointment.

```bash
git clone https://github.com/thunderbird/appointment
cp appointment/backend/.env.example appointment/backend/.env
cp appointment/frontend/.env.example appointment/frontend/.env
cd appointment
```

Next we need to pull Thunderbird Accounts. If you have a dev copy you can just symlink the folder to accounts. 

Other-wise run:

```bash
git clone https://github.com/thunderbird/thunderbird-accounts.git accounts
```

And finally we can run the service in docker:

```bash
docker-compose up -d --build
```

* Frontend can be accessed via: <http://localhost:8080>
* Backend can be accessed via: <http://localhost:5173>
* OpenAPI docs can be accessed via: <http://localhost:5173/docs> or <http://localhost:5173/redoc>

A MySQL database will be accessible via `localhost:3306` with username and password set to: `tba`

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

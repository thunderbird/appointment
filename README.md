# Thunderbird Appointment

**Note: Thunderbird Appointment is in an alpha state, so be prepared to encounter bugs**

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

### Localization

This project uses [Fluent](https://projectfluent.org/) for localization. Files are located in their respective `l10n/<locale>/*.ftl`.

### Deployment

When changes are merged to main, a new [release](https://github.com/thunderbird/appointment/releases/) is cut, and the changes are deployed to [stage.appointment.day](https://stage.appointment.day/).

After you've checked staging and it's ready to push to production, edit the release entry, and press the 'Publish release' button.

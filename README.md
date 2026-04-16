# Thunderbird Appointment

Invite others to grab times on your calendar. Choose a date. Make appointments as easy as it gets.

## Screenshots

The Bookers page for attendees and the dashboard for subscribers:

<img width="49%" alt="Thunderbird Appointment Bookers Page" src="https://github.com/user-attachments/assets/5bdde2fe-5c77-4d2a-b440-aef12d0a4d6d" />
<img width="49%" alt="Thunderbird Appointment Dashboard" src="https://github.com/user-attachments/assets/1050a0c6-10ee-4992-af9f-c20ec21a922e" />

First time user experience, Availability setup, managing bookings and general settings:

<img width="24%" alt="appointment_ftue" src="https://github.com/user-attachments/assets/56eed5b9-538a-411d-9758-c90a66e0c57e" />
<img width="24%" alt="Thunderbird Appointment Availability" src="https://github.com/user-attachments/assets/37a90df5-1825-47b8-a05f-64f3455d0e5e" />
<img width="24%" alt="Thunderbird Appointment Bookings" src="https://github.com/user-attachments/assets/4de85940-09a0-4905-965e-29f658b6bbd5" />
<img width="24%" alt="Thunderbird Appointment Settings" src="https://github.com/user-attachments/assets/fb18f443-81ae-42bb-94d3-c896f44f6aab" />

## Feedback and Support

If you'd like to give feedback or need support, please see our [Topicbox](https://thunderbird.topicbox.com/groups/services).

## Get started

Using Docker is the recommended and for now the only supported method of building and developing Thunderbird Appointment. A detailed technical documentation of the application architecture can be found in the [docs folder](./docs/README.md) (still work-in-progress).

### Installation

1. Get the application files and create your `.env` files from the examples:

    ```bash
    git clone https://github.com/thunderbird/appointment
    cd appointment
    cp backend/.env.example backend/.env
    cp frontend/.env.example frontend/.env
    ```

2. Make sure, that the `backend/.env` file contains `APP_ALLOW_FIRST_TIME_REGISTER=True`. This will enable the creation of your first admin user. If you want to be able to access admin-only pages, add your account's email address to the `APP_ADMIN_ALLOW_LIST` env variable.

3. Build and run the service in docker:

    ```bash
    docker-compose up -d --build
    ```

    This will create and start 5 different containers (backend, frontend, postgres, redis and mailpit).

    * Frontend can be accessed via: <http://localhost:8090>
    * Backend can be accessed via: <http://localhost:5000>
    * The PostgreSQL database will be accessible via `localhost:5435` with username: password set to `tba`: `abcd%efgh`
    * OpenAPI docs can be accessed via: <http://localhost:5000/docs> or <http://localhost:5000/redoc>
    * Mailpit docs can be accessed via: <http://localhost:8026>

4. Check if all containers are running. On first-run the database will initialize, and a first time setup command will be triggered (going forward database migrations will automatically run on `docker-compose up`). Check if the database contains tables, e.g. the `subscriber` table (still empty at this point).

### Authentication

Appointment includes simple password-based authentication. This is meant for developing and testing Appointment, but can also be used when self-hosting the app.

When you access the frontend the first time, you will see a first-time-user login form. Enter the email address you configured in your allow list (see Step 2 in the installation process above) and a password. This login will create the first user (also called 'subscriber' in Appointment) granting you access to the application. Any login attempts with other email addresses after that will check against existing credentials.

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

When changes are merged to main, a new [release](https://github.com/thunderbird/appointment/releases/) is cut, and the changes are deployed to [Appointment Staging](https://appointment-stage.tb.pro/).

After you've checked staging and it's ready to push to production, edit the release entry, and press the 'Publish release' button.

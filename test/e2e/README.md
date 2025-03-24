# Thunderbird Appointment E2E Tests

Guide for running the Thunderbird Appointment E2E tests.

## Installation

First install the E2E suite (includes Playwright):

```bash
cd test/e2e
npm install
```

Next install the Playwright browsers (Playwright uses it's own bundled browers) still in `test/e2e`:

```bash
npx playwright install
```

## E2E Test Prerequisites
The E2E tests require an existing Appointment (and corresponding FxA account) and associated data, and reads this from your local .env file. This includes:
- Credentials for an existing Appointment (FxA) account (email address, password)
- The account user's display name and share link:
    - The display name is found in Appointment => Settings => Account => Display name.
    - The share link is found in Appointment => Settings => Account => My Link.
- The tests also require an email address to be used as the appointment bookee's email address when actually requesting bookings. This is the email address entered on the `Book selection` dialog (after an appointment slot was selected on the booking share link page). Note that real Appointment emails will be sent to this email address.

The tests expect the following Appointment application settings:
- The user scheduling availability hasn't been changed from the default settings;
- In the dashboard the default calendar view is the current month view; this is important so that the tests can find an available booking slot, etc.
- In `Booking Settings`, the `Booking Confirmation` option is enabled, so that requested appointments generate HOLD appointments that need to be confirmed
- The timezone is set to `America/Toronto`

## Running the E2E tests against your local dev environment

First ensure that you have a local Appointment account created and you can sign in to Appointment at http://localhost:8080/.

Then copy over the provided `.env.dev.example` to a local `.env`:

```bash
cd test/e2e
cp .env.dev.example .env
```

Then edit your local `.env` file and provide the following values:
```dotenv
APPT_LOGIN_EMAIL=<existing-dev-FxA-user-email>
APPT_LOGIN_PWORD=<exisiting-dev-FxA-user-password>
APPT_DISPLAY_NAME=<appointment-dev-user-display-name>
APPT_MY_SHARE_LINK=<apointment-dev-user-share-link>
APPT_BOOKEE_EMAIL=<booking-requesters-email>
```

To run the E2E tests headless (still in `test/e2e`):

```bash
npm run e2e-test
```

To run the E2E tests with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npm run e2e-test-headed
```

To run the E2E tests in debug mode (still in `test/e2e`):

```bash
npm run e2e-test-debug
```

## Running the E2E tests against the staging environmnent

First copy over the provided `.env.stage.example` to a local `.env`:

```bash
cd test/e2e
cp .env.stage.example .env
```

Then edit your local `.env` file and provide the following values:
```dotenv
APPT_LOGIN_EMAIL=<existing-stage-FxA-user-email>
APPT_LOGIN_PWORD=<exisiting-stage-FxA-user-password>
APPT_DISPLAY_NAME=<appointment-stage-user-display-name>
APPT_MY_SHARE_LINK=<apointment-stage-user-share-link>
APPT_BOOKEE_EMAIL=<booking-requesters-email>
```

To run the E2E tests headless (still in `test/e2e`):

```bash
npm run e2e-test
```

To run the E2E tests with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npm run e2e-test-headed
```

To run the E2E tests in debug mode (still in `test/e2e`):

```bash
npm run e2e-test-debug
```

## Running the production sanity test

First copy over the provided `.env.prod.example` to a local `.env`:

```bash
cd test/e2e
cp .env.prod.example .env
```

Then edit your local `.env` file and provide the following values:
```dotenv
APPT_LOGIN_EMAIL=<existing-prod-FxA-user-email>
APPT_LOGIN_PWORD=<exisiting-prod-FxA-user-password>
APPT_DISPLAY_NAME=<appointment-prod-user-display-name>
APPT_MY_SHARE_LINK=<apointment-prod-user-share-link>
APPT_BOOKEE_EMAIL=<booking-requesters-email>
```

To run the production sanity test headless (still in `test/e2e`):

```bash
npm run prod-sanity-test
```

To run the production sanity test with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npm run prod-sanity-test-headed
```

To run the production sanity test in debug mode (still in `test/e2e`):

```bash
npm run prod-sanity-test-debug
```

## Running on BrowserStack

You can run the E2E tests from your local machine but against browsers provided in the BrowserStack Automate cloud.

<b>For security reasons when running the tests on BrowserStack I recommend that you use a dedicated test Appointment FxA account / credentials (NOT your own personal Appointment (FxA) credentials).</b>

Once you have credentials for an existing Appointemnt test account, edit your local `.env` file and add these details (more information found above):

```dotenv
APPT_LOGIN_EMAIL=<existing-test-FxA-user-email>
APPT_LOGIN_PWORD=<exisiting-test-FxA-user-password>
APPT_DISPLAY_NAME=<appointment-user-display-name>
APPT_MY_SHARE_LINK=<apointment-user-share-link>
APPT_BOOKEE_EMAIL=<booking-requesters-email>
```

Also in order to run on BrowserStack you need to provide your BrowserStack credentials. Sign into your BrowserStack account and navigate to your `User Profile` and find your auth username and access key. In your local terminal export the following env vars to set the BrowserStack credentials that the tests will use:

```bash
export BROWSERSTACK_USERNAME=<your-browserstack-user-name>
```

```bash
export BROWSERSTACK_ACCESS_KEY=<your-browserstack-access-key>
```

To run the E2E tests on BrowserStack (still in `test/e2e`):

```bash
npm run e2e-test-browserstack
```

To run the production sanity test on BrowserStack (still in `test/e2e`):

```bash
npm run prod-sanity-test-browserstack
```

After the tests finish in your local console you'll see a link to the BrowserStack test session; when signed into your BrowserStack account you'll be able to use that link to see the test session results including video playback.

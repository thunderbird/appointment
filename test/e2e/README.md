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

## Running the E2E tests on mobile browsers
The E2E tests can also be run on mobile browsers (against production Appointment) but only on BrowserStack (NOT on local mobile devices). There is a separate `nigtly-tests-mobile` GitHub Actions job that runs nighlty but can also be triggered manually via the GitHub actions tab, against whichever branch you choose.

You can also run the E2E tests on a mobile browser (against production Appointment) on BrowserStack from your local machine; this is handy if you're making changes to the actual E2E tests themselves on your local stack. To do that follow the `Running on BrowserStack` steps above, but use this command line to start the tests:

```bash
npm run prod-nightly-tests-mobile-browserstack-gha
```

## Debugging E2E Test Failures

Here is some advice for how to investigate E2E test failures.

### E2E Tests Failing on your Local Dev Environment
If you are running the E2E tests on your local machine against your local development environment and the tests are failing, you can:
- Run the tests again this time in debug (UI) mode (see above)
    - In the debug mode browser expand each test that was ran, and review each test step to trace the test progress and failure
    - Look at the corresponding screenshots to get a visual of where and when the tests actually failed
    - Try to correlate the test failure with any local code changes

### E2E Tests Failing in CI on your PR Check
If you pushed to a branch or PR and the resulting Github pull request E2E test job check is failing, you can:

- In your PR scroll down to the 'Checks' section and click on the failed E2E test job
- In the console view, expand the E2E tests step and read the test failure details
- Check if a playwright report artifact exists:
    - In the console view click on `Summary` (top left)
    - This shows the GHA summary, at the bottom of the page look for an `Artifacts` section and click on `playwright-report` and download the ZIP
    - Open the ZIP file, expand it, and open the `index.html` file in your browser

### E2E Tests Failing in CI after a Deployment to Stage or Production
If you did a stage or production deployment and the resulting E2E tests job failed, you can:

- Go into the Github repo, and
    - Choose `Actions` at the top
    - On the list of Actions on the left side choose the one matching your stage or production deployment
    - In the corresponding list of completed action jobs, click on the failing one
    - Then click on the failed E2E test step to open the console view
    - In the console view, expand the E2E tests job and read the test failure details
    - The tests run in BrowserStack which records a video playback of all of the tests
        - In the console view search the logs for the string `View build on BrowserStack dashboard` and retrieve the associated BrowserStack session link
        - Click on the link and sign into BrowserStack with your credentials and view the video replay of the failing test

### Nightly E2E Tests CI Job Failing
If you notice an email from Github actions indicating that the Nightly E2E Tests job failed, you can:

- Open the failing Github nightly-tests action job:
    - Click on the `View workflow run` link in the email - or -
    - Go into the Github repo, and
        - Choose `Actions` at the top
        - Depending on what platform is failing, on the list of Actions on the left side choose `nightly-tests-desktop` or `nightly-tests-mobile`
        - In the corresponding list of completed nightly test action jobs, click on the failing one
    - Then click on the failed E2E test step to open the console view
    - In the console view, expand the E2E tests job and read the test failure details
    - The nightly tests run in BrowserStack which records a video playback of all of the tests
        - In the console view search the logs for the string `View build on BrowserStack dashboard` and retrieve the associated BrowserStack session link
        - Click on the link and sign into BrowserStack with your credentials and view the video replay of the failing test

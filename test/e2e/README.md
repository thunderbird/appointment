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

The E2E tests require an existing TB Pro account and other settings that are read this from your local .env file. This includes:
- Credentials for an existing TB Pro account (TB Pro email and associated password)
- The account user's display name and share link:
    - The display name is found in Appointment => Settings => Account => Display name.
    - The share link is found in Appointment => Settings => Account => My Link.
- The tests also require an email address to be used as the appointment bookee's email address when actually requesting bookings. This is the email address entered on the `Book selection` dialog (after an appointment slot was selected on the booking share link page). Note that real Appointment emails will be sent to this email address.

The tests expect the following Appointment application settings:
- The user scheduling availability hasn't been changed from the default settings;
- In the dashboard the default calendar view is the current month view; this is important so that the tests can find an available booking slot, etc.
- In `Booking Settings`, the `Automatically confirm bookings if time is available` option is checked / turned on

## Running the E2E tests against your local dev environment

First ensure that you have a local Appointment account created and you can sign in to Appointment at http://localhost:8080/.

Then copy over the provided `.env.dev.example` to a local `.env`:

```bash
cd test/e2e
cp .env.dev.example .env
```

Then edit your local `.env` file and provide the following values:
```dotenv
TB_ACCTS_EMAIL=<existing-local-account-user-email>
TB_ACCTS_PWORD=<exisiting-local-user-password>
APPT_DISPLAY_NAME=<appointment-dev-user-display-name>
APPT_MY_SHARE_LINK=<apointment-dev-user-share-link>
APPT_BOOKEE_EMAIL=<booking-requesters-email>
```

To run the E2E tests on Firefox headless (still in `test/e2e`):

```bash
npm run e2e-test
```

To run the E2E tests on Firefox with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npm run e2e-test-headed
```

To run the E2E tests against google chromium with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npx playwright test --grep e2e-suite --project=chromium --headed
```

To run the E2E tests against safari with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npx playwright test --grep e2e-suite --project=safari --headed
```

Note that for project you can use any of the project/browser names as listed in the [playwright.config.ts](./playwright.config.ts) file (but the browser must be installed on your local machine).

## Running on a Local Playwright Emulated Mobile Browser View

You can run the E2E tests on your local machine on emulated mobile browser views provided by Playwright (as installed above). Note: This is not a real device emulator, it just uses a local plawyright browser and sets the browser screen size to match a mobile device, etc. More info about mobile emulation [is here](https://playwright.dev/docs/emulation).

To run the E2E tests on an emulated Google Pixel 7 mobile browser view (still in `test/e2e`):

```bash
npx playwright test --grep e2e-mobile-suite --project=Google-Pixel-7-View --headed
```

Note that for project you can use any of the project/browser names as listed in the [playwright.config.ts](./playwright.config.ts) file (but the browser must be installed on your local machine).

## Running the E2E tests against the staging environmnent

First copy over the provided `.env.stage.example` to a local `.env`:

```bash
cd test/e2e
cp .env.stage.example .env
```

Then edit your local `.env` file and provide the following values:
```dotenv
TB_ACCTS_EMAIL=<existing-stage-tb-accounts-user-email>
TB_ACCTS_PWORD=<exisiting-stage-tb-accounts-user-password>
APPT_DISPLAY_NAME=<appointment-stage-user-display-name>
APPT_MY_SHARE_LINK=<apointment-stage-user-share-link>
APPT_BOOKEE_EMAIL=<booking-requesters-email>
```

To run the E2E tests on Firefox headless (still in `test/e2e`):

```bash
npm run e2e-test
```

To run the E2E tests on Firefox with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npm run e2e-test-headed
```

## Running the production sanity test

First copy over the provided `.env.prod.example` to a local `.env`:

```bash
cd test/e2e
cp .env.prod.example .env
```

Then edit your local `.env` file and provide the following values:
```dotenv
TB_ACCTS_EMAIL=<existing-prod-tb-accounts-user-email>
TB_ACCTS_PWORD=<exisiting-prod-tb-accounts-user-password>
APPT_DISPLAY_NAME=<appointment-prod-user-display-name>
APPT_MY_SHARE_LINK=<apointment-prod-user-share-link>
APPT_BOOKEE_EMAIL=<booking-requesters-email>
```

To run the production sanity test on Firefox headless (still in `test/e2e`):

```bash
npm run prod-sanity-test
```

To run the production sanity test on Firefox with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npm run prod-sanity-test-headed
```

## Running on BrowserStack

You can run the E2E tests from your local machine but against browsers provided in the BrowserStack Automate cloud.

<b>For security reasons when running the tests on BrowserStack I recommend that you use a dedicated test Appointment account / credentials (NOT your own personal Appointment credentials).</b>

Once you have credentials for an existing TB Pro test account, edit your local `.env` file and add these details (more information found above):

```dotenv
TB_ACCTS_EMAIL=<existing-tb-accounts-user-email>
TB_ACCTS_PWORD=<exisiting-tb-accounts-user-password>
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

To run the E2E tests on mobile devices on BrowserStack (still in `test/e2e`):

```bash
npm run e2e-test-mobile-browserstack
```

To run the nightly test suite on real mobile devices in BrowserStack (still in `test/e2e`):

```bash
npm run prod-nightly-tests-mobile-browserstack-gha
```

After the tests finish in your local console you'll see a link to the BrowserStack test session; when signed into your BrowserStack account you'll be able to use that link to see the test session results including video playback.

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
        - On the list of Actions on the left side choose `nightly-tests-desktop`
        - In the corresponding list of completed nightly test action jobs, click on the failing one
    - Then click on the failed E2E test step to open the console view
    - In the console view, expand the E2E tests job and read the test failure details
    - The nightly tests run in BrowserStack which records a video playback of all of the tests
        - In the console view search the logs for the string `View build on BrowserStack dashboard` and retrieve the associated BrowserStack session link
        - Click on the link and sign into BrowserStack with your credentials and view the video replay of the failing test

# Thunderbird Appointment E2E Tests

Guide for running the Thunderbird Appointment E2E tests.

## Prerequisite

You must have a pre-existing Appointment user test account (using FxA credentials) on the platform where you are running the tests. ie. For the production sanity test you must have an Appointment test account on production (using production FxA credentials) already set up.

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

## Running Locally

The E2E tests require credentials for an existing Appointment (FxA) account and reads these from your local env vars. First copy over the provided `.example.env` to a local `.env`:

```bash
cd test/e2e
cp .env.example .env
```

Then edit your local `.env` file and provide the credentials for your Appointment test account:

`APPT_PROD_LOGIN_EMAIL=<existing-test-FxA-user-email>`</br>
`APPT_PROD_LOGIN_PWORD=<exisiting-test-FxA-user-password>`

To run the production sanity test headless (still in `test/e2e`):

```bash
npm run prod-sanity-test
```

To run the production sanity test with a UI so you can watch the tests run (still in `test/e2e`):

```bash
npm run prod-sanity-test-ui
```

To run the production sanity test in debug mode (still in `test/e2e`):

```bash
npm run prod-sanity-test-debug
```

## Running on BrowserStack

You can run the E2E tests from your local machine but against browsers provided in the BrowserStack Automate cloud.

<b>For security reasons when running the tests on BrowserStack I recommend that you use a dedicated test Appointment FxA account / credentials (NOT your own personal Appointment (FxA) credentials).</b>

Once you have credentials for an existing Appointemnt test account, edit your local `.env` file and add the credentials:

`APPT_PROD_LOGIN_EMAIL=<existing-test-FxA-user-email>`</br>
`APPT_PROD_LOGIN_PWORD=<exisiting-test-FxA-user-password>`

Also in order to run on BrowserStack you need to provide your BrowserStack credentials. Sign into your BrowserStack account and navigate to your `User Profile` and find your auth username and access key. In your local terminal export the following env vars to set the BrowserStack credentials that the tests will use:

```bash
export BROWSERSTACK_USERNAME=<your-browserstack-user-name>
```

```bash
export BROWSERSTACK_ACCESS_KEY=<your-browserstack-access-key>
```

To run the production sanity test on BrowserStack (still in `test/e2e`):

```bash
npm run prod-sanity-test-browserstack
```

After the tests finish in your local console you'll see a link to the BrowserStack test session; when signed into your BrowserStack account you'll be able to use that link to see the test session results including video playback.

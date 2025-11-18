// environment where the tests will run
export const APPT_TARGET_ENV = String(process.env.APPT_TARGET_ENV);

// appointment urls
export const APPT_URL = String(process.env.APPT_URL);
export const APPT_MY_SHARE_LINK = String(process.env.APPT_MY_SHARE_LINK);
export const APPT_SHORT_SHARE_LINK_PREFIX = String(process.env.APPT_SHORT_SHARE_LINK_PREFIX);
export const APPT_LONG_SHARE_LINK_PREFIX = String(process.env.APPT_LONG_SHARE_LINK_PREFIX);
export const APPT_BOOKINGS_PAGE = String(`${process.env.APPT_URL}bookings`);
export const APPT_SETTINGS_PAGE = String(`${process.env.APPT_URL}settings`);
export const APPT_DASHBOARD_HOME_PAGE = String(`${process.env.APPT_URL}dashboard`);
export const APPT_DASHBOARD_MONTH_PAGE = String(`${process.env.APPT_URL}dashboard#month`);
export const APPT_AVAILABILITY_PAGE = String(`${process.env.APPT_URL}availability`);

// page titles
export const APPT_PAGE_TITLE = 'Thunderbird Appointment';
export const TB_ACCTS_PAGE_TITLE = 'Sign in to Thunderbird';

// sign-in credentials
export const TB_ACCTS_EMAIL = String(process.env.TB_ACCTS_EMAIL);
export const TB_ACCTS_PWORD = String(process.env.TB_ACCTS_PWORD);

// appointment user display name (settings => account) for above user
export const APPT_DISPLAY_NAME = String(process.env.APPT_DISPLAY_NAME);

// appointment requester's name and email address
export const APPT_BOOKEE_NAME = String(process.env.APPT_BOOKEE_NAME);
export const APPT_BOOKEE_EMAIL = String(process.env.APPT_BOOKEE_EMAIL);

// playwright test tags
export const PLAYWRIGHT_TAG_PROD_SANITY = '@prod-sanity';
export const PLAYWRIGHT_TAG_E2E_SUITE = '@e2e-suite';
export const PLAYWRIGHT_TAG_PROD_NIGHTLY = '@prod-nightly';
export const PLAYWRIGHT_TAG_E2E_SUITE_MOBILE = '@e2e-mobile-suite';
export const PLAYWRIGHT_TAG_PROD_MOBILE_NIGHTLY = '@prod-mobile-nightly';

// general settings options
export const APPT_LANGUAGE_SETTING_EN = 'EN — English';
export const APPT_LANGUAGE_SETTING_DE = 'DE — German';
export const APPT_THEME_SETTING_LIGHT = 'Light';
export const APPT_THEME_SETTING_DARK = 'Dark';
// set the Appointment time zone setting to the local timezone is where the test is running
export const APPT_TIMEZONE_SETTING_PRIMARY = Intl.DateTimeFormat().resolvedOptions().timeZone;
console.log(`using local timezone: ${APPT_TIMEZONE_SETTING_PRIMARY}`)
export const APPT_TIMEZONE_SETTING_HALIFAX = 'America/Halifax'; // settings test changes to this tz temporarily
export const APPT_START_OF_WEEK_SUN = 'S';
export const APPT_START_OF_WEEK_MON = 'M';
export const APPT_START_OF_WEEK_DASHBOARD_SUN = 'Sun';
export const APPT_START_OF_WEEK_DASHBOARD_MON = 'Mon';

// local browser store values
export const APPT_BROWSER_STORE_LANGUAGE_EN = 'en';
export const APPT_BROWSER_STORE_LANGUAGE_DE = 'de';
export const APPT_BROWSER_STORE_THEME_LIGHT = 'light';
export const APPT_BROWSER_STORE_THEME_DARK = 'dark';
export const APPT_BROWSER_STORE_12HR_TIME = 12;
export const APPT_BROWSER_STORE_START_WEEK_SUN = 7;
export const APPT_BROWSER_STORE_START_WEEK_MON = 1;

// html class attribute value when dark mode is enabled
export const APPT_HTML_DARK_MODE_CLASS = 'dark';

// timeouts
export const TIMEOUT_1_SECOND = 1_000;
export const TIMEOUT_2_SECONDS = 2_000;
export const TIMEOUT_3_SECONDS = 3_000;
export const TIMEOUT_5_SECONDS = 5_000;
export const TIMEOUT_10_SECONDS = 10_000;
export const TIMEOUT_15_SECONDS = 15_000;
export const TIMEOUT_30_SECONDS = 30_000;
export const TIMEOUT_60_SECONDS = 60_000;
export const TIMEOUT_90_SECONDS = 90_000;

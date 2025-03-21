// environment where the tests will run
export const APPT_TARGET_ENV = String(process.env.APPT_TARGET_ENV);

// appointment urls
export const APPT_URL = String(process.env.APPT_URL);
export const APPT_MY_SHARE_LINK = String(process.env.APPT_MY_SHARE_LINK);
export const APPT_SHORT_SHARE_LINK_PREFIX = String(process.env.APPT_SHORT_SHARE_LINK_PREFIX);
export const APPT_LONG_SHARE_LINK_PREFIX = String(process.env.APPT_LONG_SHARE_LINK_PREFIX);
export const APPT_PENDING_BOOKINGS_PAGE = String(`${process.env.APPT_URL}bookings/pending`);
export const APPT_BOOKED_BOOKINGS_PAGE = String(`${process.env.APPT_URL}bookings/booked`);
export const APPT_MAIN_SETTINGS_PAGE = String(`${process.env.APPT_URL}settings`);
export const APPT_GENERAL_SETTINGS_PAGE = String(`${process.env.APPT_URL}settings/general`);
export const APPT_CALENDAR_SETTINGS_PAGE = String(`${process.env.APPT_URL}settings/calendar`);
export const APPT_ACCOUNT_SETTINGS_PAGE = String(`${process.env.APPT_URL}settings/account`);
export const APPT_CONNECTED_SETTINGS_PAGE = String(`${process.env.APPT_URL}settings/connectedAccounts`);
export const APPT_DASHBOARD_MONTH_PAGE = String(`${process.env.APPT_URL}dashboard#month`);

// page titles
export const APPT_PAGE_TITLE = 'Thunderbird Appointment';
export const FXA_PAGE_TITLE = 'Mozilla accounts';

// sign-in credentials and corresponding account display name
export const APPT_LOGIN_EMAIL = String(process.env.APPT_LOGIN_EMAIL);
export const APPT_LOGIN_PWORD = String(process.env.APPT_LOGIN_PWORD);

// appointment user display name (settings => account) for above user
export const APPT_DISPLAY_NAME = String(process.env.APPT_DISPLAY_NAME);

// appointment requester's name and email address
export const APPT_BOOKEE_NAME = String(process.env.APPT_BOOKEE_NAME);
export const APPT_BOOKEE_EMAIL = String(process.env.APPT_BOOKEE_EMAIL);

// playwright test tags
export const PLAYWRIGHT_TAG_PROD_SANITY = '@prod-sanity';
export const PLAYWRIGHT_TAG_E2E_SUITE = '@e2e-suite';

// general settings options
export const APPT_LANGUAGE_SETTING_EN = 'EN — English';
export const APPT_LANGUAGE_SETTING_DE = 'DE — German';
export const APPT_THEME_SETTING_LIGHT = 'Light';
export const APPT_THEME_SETTING_DARK = 'Dark';
export const APPT_TIMEZONE_SETTING_TORONTO = 'America/Toronto';
export const APPT_TIMEZONE_SETTING_HALIFAX = 'America/Halifax';

// local browser store values
export const APPT_BROWSER_STORE_LANGUAGE_EN = 'en';
export const APPT_BROWSER_STORE_LANGUAGE_DE = 'de';
export const APPT_BROWSER_STORE_THEME_LIGHT = 'light';
export const APPT_BROWSER_STORE_THEME_DARK = 'dark';
export const APPT_BROWSER_STORE_12HR_TIME = 12;
export const APPT_BROWSER_STORE_24HR_TIME = 24;

// html class attribute value when dark mode is enabled
export const APPT_HTML_DARK_MODE_CLASS = 'dark';

// timeouts
export const TIMEOUT_2_SECONDS = 2_000;
export const TIMEOUT_3_SECONDS = 3_000;
export const TIMEOUT_30_SECONDS = 30_000;
export const TIMEOUT_60_SECONDS = 60_000;

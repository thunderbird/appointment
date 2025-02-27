// environment where the tests will run
export const APPT_TARGET_ENV = String(process.env.APPT_TARGET_ENV);

// appointment urls
export const APPT_URL = String(process.env.APPT_URL);
export const APPT_MY_SHARE_LINK = String(process.env.APPT_MY_SHARE_LINK);
export const APPT_SHORT_SHARE_LINK_PREFIX = String(process.env.APPT_SHORT_SHARE_LINK_PREFIX);
export const APPT_LONG_SHARE_LINK_PREFIX = String(process.env.APPT_LONG_SHARE_LINK_PREFIX);
export const APPT_PENDING_BOOKINGS_PAGE = `${process.env.APPT_URL}bookings/pending`;
export const APPT_BOOKED_BOOKINGS_PAGE = `${process.env.APPT_URL}bookings/booked`;

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

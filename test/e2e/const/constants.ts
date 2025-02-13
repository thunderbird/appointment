// appointment urls
export const APPT_URL = String(process.env.APPT_URL);
export const APPT_MY_SHARE_LINK = String(process.env.APPT_MY_SHARE_LINK);
export const APPT_SHORT_SHARE_LINK_PREFIX = String(process.env.APPT_SHORT_SHARE_LINK_PREFIX);
export const APPT_LONG_SHARE_LINK_PREFIX = String(process.env.APPT_LONG_SHARE_LINK_PREFIX);
export const APPT_PROD_PENDING_BOOKINGS_PAGE = `${process.env.APPT_URL}bookings/pending`;

// page titles
export const APPT_PAGE_TITLE = 'Thunderbird Appointment';
export const FXA_PAGE_TITLE = 'Mozilla accounts';

// production sign-in credentials and corresponding account display name
export const PROD_LOGIN_EMAIL = String(process.env.APPT_LOGIN_EMAIL);
export const PROD_LOGIN_PWORD = String(process.env.APPT_LOGIN_PWORD);

// appointment user display name (settings => account) for above user
export const PROD_DISPLAY_NAME = String(process.env.APPT_DISPLAY_NAME);

// appointment requester's name and email address
export const APPT_BOOKING_REQUESTER_NAME = String(process.env.APPT_BOOKING_REQUESTER_NAME);
export const APPT_BOOKING_REQUESTER_EMAIL = String(process.env.APPT_BOOKING_REQUESTER_EMAIL);

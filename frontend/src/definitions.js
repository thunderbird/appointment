/**
 * Available date format strings
 * @readonly
 * @enum
 */
export const dateFormatStrings = {
  // Qalendar specific formats (These have to be in this format for qalendar to understand them)
  qalendar: 'YYYY-MM-DD HH:mm',
  qalendarFullDay: 'YYYY-MM-DD',
  // Time display formats
  display12Hour: 'hh:mma',
  display24Hour: 'HH:mm',
};

/**
 * The amount of time in minutes a schedule's slot duration will default to
 * @type {number}
 */
export const defaultSlotDuration = 30;

/**
 * Appointment subscriber levels
 * @enum
 * @readonly
 */
export const subscriberLevels = {
  basic: 1,
  plus: 2,
  pro: 3,
  admin: 99,
};

/**
 * Appointment location types for schedules
 * @enum
 * @readonly
 */
export const locationTypes = {
  inPerson: 1,
  online: 2,
};

/**
 * Appointment creation state
 * @enum
 * @readonly
 */
export const appointmentCreationState = {
  hidden: 0,
  details: 1,
  availability: 2,
  finished: 3,
};

/**
 * Schedule creation state
 * @enum
 * @readonly
 */
export const scheduleCreationState = {
  details: 1,
  availability: 2,
  settings: 3,
};

/**
 * Calendar view mode
 * @enum
 * @readonly
 */
export const calendarViews = {
  day: 1,
  week: 2,
  month: 3,
};

/**
 * Booking calendar view modes
 * @enum
 * @readonly
 */
export const bookingCalendarViews = {
  ...calendarViews,
  weekAfterMonth: 4,
  loading: 10,
  success: 11,
  invalid: 12,
};

/**
 * Booking status for slots. This mirrors models.BookingStatus on the backend
 * @enum
 * @readonly
 */
export const bookingSlotStatus = {
  none: 1,
  requested: 2,
  booked: 3,
};

/**
 * Available appointment states
 * @enum
 * @readonly
 */
export const appointmentState = {
  booked: 1,
  pending: 2,
  past: 3,
};

/**
 * Available appointment views
 * @enum
 * @readonly
 */
export const appointmentViews = {
  ...appointmentState,
  all: 4,
};

/**
 * List columns for bookings page
 * @enum
 * @readonly
 */
export const listColumns = {
  title: 1,
  status: 2,
  active: 3,
  calendar: 4,
  bookingLink: 5,
  replies: 6,
};

/**
 * Filter options for bookings page
 * @enum
 * @readonly
 */
export const filterOptions = {
  allAppointments: 1,
  appointmentsToday: 2,
  appointmentsNext7Days: 3,
  appointmentsNext14Days: 4,
  appointmentsNext31Days: 5,
  appointmentsInMonth: 6,
  allFutureAppointments: 7,
};

/**
 * View types for the bookings page
 * @enum
 * @readonly
 */
export const viewTypes = {
  list: 1,
  grid: 2,
};

/**
 * Settings page sections
 * @enum
 * @readonly
 */
export const settingsSections = {
  general: 1,
  calendar: 2,
  // appointmentsAndBooking: 3,
  account: 4,
  // privacy:                5,
  // faq:                    6,
};

/**
 * available color schemes for theme
 * @readonly
 * @enum
 */
export const colorSchemes = {
  system: 1,
  dark: 2,
  light: 3,
};

/**
 * Calendar management type states
 * @enum
 * @readonly
 */
export const calendarManagementType = {
  connect: 1,
  edit: 2,
};

/**
 * Meeting provider types (matches the backends version)
 * @enum
 * @readonly
 */
export const meetingLinkProviderType = {
  none: 'none',
  zoom: 'zoom',
  google_meet: 'google_meet',
};

/**
 * Model states
 * @enum
 * @readonly
 */
export const modalStates = {
  loading: 1, // Modal is loading, this includes submission requests
  open: 2, // Modal is open for editing
  error: 3, // Modal is open for editing but contains errors
  finished: 4, // Modal is finished, so either self-close, or show a success screen
};

/**
 * Alert levels
 * @enum
 * @readonly
 */
export const alertSchemes = {
  error: 1, // Alert indicates something's gone wrong
  warning: 2, // Alert indicates something important
  success: 3, // Alert indicates something's gone right
  info: 4, // Alert indicates some neutral information
};

/**
 * Only available duration values supported for Qalendar
 * This defines basically the number of intervals there will be.
 * See: https://tomosterlund.github.io/qalendar/guide.html#intervals
 * @enum
 * @readonly
 */
export const qalendarSlotDurations = {
  15: 15,
  30: 30,
  60: 60,
};

/**
 * Used as the session storage key for the location the user wanted to go to before logging in.
 * @type {string}
 */
export const loginRedirectKey = 'loginRedirect';

export default {
  subscriberLevels,
  appointmentState,
  appointmentViews,
  bookingCalendarViews,
  calendarViews,
  colorSchemes,
  scheduleCreationState,
  filterOptions,
  listColumns,
  locationTypes,
  settingsSections,
  viewTypes,
  meetingLinkProviderType,
  dateFormatStrings,
  qalendarSlotDurations,
};

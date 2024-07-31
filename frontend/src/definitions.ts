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
  availability: 1,
  settings: 2,
  details: 3,
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
 */
export enum BookingCalendarViews {
  Day = 1,
  Week = 2,
  Month = 3,
  WeekAfterMonth = 4,
  Loading = 10,
  Success = 11,
  Invalid = 12,
};

/**
 * Booking status for slots. This mirrors models.BookingStatus on the backend
 * @enum
 * @readonly
 */
export const bookingStatus = {
  none: 1,
  requested: 2,
  booked: 3,
};

/**
 * Status to indicate if an invite code ist still valid or no longer valid
 */
export enum InviteStatus {
  Active = 1,
  Revoked = 2,
};

// available appointment views
export const appointmentViews = {
  booked: 1,
  pending: 2,
  past: 3,
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
  // active: 3,
  calendar: 3,
  time: 4,
  // bookingLink: 4,
  // replies: 4,
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
  account: 3,
  connectedAccounts: 4,
};

/**
 * Available color schemes for theme
 */
export enum ColorSchemes {
  System = 'system',
  Dark = 'dark',
  Light = 'light',
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
 */
export enum ModalStates {
  Loading = 1, // Modal is loading, this includes submission requests
  Open = 2, // Modal is open for editing
  Error = 3, // Modal is open for editing but contains errors
  Finished = 4, // Modal is finished, so either self-close, or show a success screen
};

/**
 * Alert levels
 * @enum
 * @readonly
 */
export enum AlertSchemes {
  Error = 1, // Alert indicates something's gone wrong
  Warning = 2, // Alert indicates something important
  Success = 3, // Alert indicates something's gone right
  Info = 4, // Alert indicates some neutral information
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

/**
 * Data types for table row items
 * @enum
 * @readonly
 */
export const tableDataType = {
  text: 1,
  link: 2,
  button: 3,
  code: 4,
  bool: 5,
};

/**
 * @enum
 * @readonly
 */
export const tableDataButtonType = {
  primary: 1,
  secondary: 2,
  caution: 3,
};

/**
 * First Time User Experience Steps
 * Step amounts are 10-based to allow us flexibility in adding steps later.
 * @enum
 * @readonly
 */
export const ftueStep = {
  setupProfile: 10,
  // Right now we only support Google calendars during ftue
  googlePermissions: 20,
  connectCalendars: 30,
  setupSchedule: 40,
  connectVideoConferencing: 50,
  finish: 100,
};

/**
 *
 * @enum
 * @readonly
 */
export const tooltipPosition = {
  none: 'pos-none',
  top: 'pos-top',
  bottom: 'pos-bottom',
  left: 'pos-left',
  right: 'pos-right',
};

/**
 * This should match the enum in routes/waiting_list.py
 * @enum
 * @readonly
 */
export const waitingListAction = {
  confirm: 1,
  leave: 2,
};

export default {
  AlertSchemes,
  appointmentCreationState,
  appointmentViews,
  BookingCalendarViews,
  bookingStatus,
  calendarManagementType,
  calendarViews,
  ColorSchemes,
  dateFormatStrings,
  defaultSlotDuration,
  filterOptions,
  ftueStep,
  InviteStatus,
  listColumns,
  locationTypes,
  loginRedirectKey,
  meetingLinkProviderType,
  ModalStates,
  qalendarSlotDurations,
  scheduleCreationState,
  settingsSections,
  subscriberLevels,
  tableDataButtonType,
  tableDataType,
  tooltipPosition,
  viewTypes,
  waitingListAction,
};

/**
 * @deprecated Use DateFormatStrings enum instead
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
 * Available date format strings
 */
export enum DateFormatStrings {
  // Qalendar specific formats (These have to be in this format for qalendar to understand them)
  Qalendar = 'YYYY-MM-DD HH:mm',
  QalendarFullDay = 'YYYY-MM-DD',
  // Time display formats
  Display12Hour = 'hh:mma',
  Display24Hour = 'HH:mm',
}

/**
 * The amount of time in minutes a schedule's slot duration will default to
 */
export const defaultSlotDuration = 30;

/**
 * Appointment subscriber levels
 */
export enum SubscriberLevels {
  Basic = 1,
  Plus = 2,
  Pro = 3,
  Admin = 99,
}

/**
 * @deprecated use EventLocationType
 */
export const locationTypes = {
  inPerson: 1,
  online: 2,
};

/**
 * Schedule creation state
 */
export enum ScheduleCreationState {
  Availability = 1,
  Settings = 2,
  Details = 3,
}

/**
 * Booking calendar view modes
 */
export enum BookingCalendarView {
  Day = 1,
  Week = 2,
  Month = 3,
  WeekAfterMonth = 4,
  Loading = 10,
  Success = 11,
  Invalid = 12,
}

/**
 * Booking status for slots. This mirrors models.BookingStatus on the backend
 */
export enum BookingStatus {
  None = 1,
  Requested = 2,
  Booked = 3,
}

/**
 * Status to indicate if an invite code ist still valid or no longer valid
 */
export enum InviteStatus {
  Active = 1,
  Revoked = 2,
}

/**
 * Available appointment views
 */
export enum BookingsViews {
  Booked = 1,
  Pending = 2,
  Past = 3,
  All = 4,
}

/**
 * List columns for bookings page
 */
export enum BookingsTableColumns {
  Title = 1,
  Status = 2,
  Calendar = 3,
  Time = 4,
}

/**
 * Filter options for bookings page
 */
export enum BookingsTableFilterOptions {
  AllAppointments = 1,
  AppointmentsToday = 2,
  AppointmentsNext7Days = 3,
  AppointmentsNext14Days = 4,
  AppointmentsNext31Days = 5,
  AppointmentsInMonth = 6,
  AllFutureAppointments = 7,
}

/**
 * View types for the bookings page
 */
export enum BookingsViewTypes {
  List = 1,
  Grid = 2,
}


/**
 * Type for event location.
 * Corresponds to models.LocationType
 */
export enum EventLocationType {
  InPerson = 1,
  Online = 2,
}

/**
 * Settings page sections
 */
export enum SettingsSections {
  General = 1,
  Calendar = 2,
  Account = 3,
  ConnectedAccounts = 4,
}

/**
 * Available color schemes for theme
 */
export enum ColorSchemes {
  System = 'system',
  Dark = 'dark',
  Light = 'light',
}

/**
 * Calendar management type states
 */
export enum CalendarManagementType {
  Connect = 1,
  Edit = 2,
}

/**
 * Supported calendar providers
 */
export enum CalendarProviders {
  Caldav = 1,
  Google = 2,
}

/**
 * Supported external connection providers
 */
export enum ExternalConnectionProviders {
  Fxa = 1,
  Google = 2,
  Zoom = 3,
}

/**
 * @deprecated Use MeetingLinkProviderType instead
 */
export const meetingLinkProviderType = {
  none: 'none',
  zoom: 'zoom',
  google_meet: 'google_meet',
};
/**
 * Meeting provider types (matches the backends version)
 */
export enum MeetingLinkProviderType {
  None = 'none',
  Zoom = 'zoom',
  GoogleMeet = 'google_meet',
}

/**
 * Model states
 */
export enum ModalStates {
  Loading = 1, // Modal is loading, this includes submission requests
  Open = 2, // Modal is open for editing
  Error = 3, // Modal is open for editing but contains errors
  Finished = 4, // Modal is finished, so either self-close, or show a success screen
}

/**
 * Alert levels
 */
export enum AlertSchemes {
  Error = 1, // Alert indicates something's gone wrong
  Warning = 2, // Alert indicates something important
  Success = 3, // Alert indicates something's gone right
  Info = 4, // Alert indicates some neutral information
};

/**
 * Used as the session storage key for the location the user wanted to go to before logging in.
 */
export const loginRedirectKey = 'loginRedirect';

/**
 * Data types for table row items
 */
export enum TableDataType {
  Text = 1,
  Link = 2,
  Button = 3,
  Code = 4,
  Bool = 5,
}

/**
 * Button types for table data fields
 */
export enum TableDataButtonType {
  Primary = 1,
  Secondary = 2,
  Caution = 3,
}

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
 */
export enum WaitingListAction {
  Confirm = 1,
  Leave = 2,
};

export enum MetricEvents {
  PageLoaded = 'apmt.page.loaded',
  FTUEStep = 'apmt.ftue.step',
  CopyToClipboard = 'apmt.copy',
  AddCalendar = 'apmt.calendar.add',
  EditCalendar = 'apmt.calendar.edit',
  DeleteCalendar = 'apmt.calendar.delete',
  ConnectCalendar = 'apmt.calendar.connect',
  DisconnectCalendar = 'apmt.calendar.disconnect',
  SyncCalendars = 'apmt.calendar.sync',
  RefreshLink = 'apmt.account.refreshLink',
  DownloadData = 'apmt.account.download',
  DeleteAccount = 'apmt.account.delete',
  ConfirmBooking = 'apmt.booking.confirm',
  DenyBooking = 'apmt.booking.deny',
  RequestBooking = 'apmt.booking.request',
  ScheduleCreated = 'apmt.schedule.created',
  ScheduleUpdated = 'apmt.schedule.updated',
  SignUp = 'apmt.signup',
  SignUpAlreadyExists = 'apmt.signup.already-exists',
  Login = 'apmt.login',
  WaitingListEmailConfirmed = 'apmt.signup.email-confirmed',
  WaitingListEmailRemoved = 'apmt.signup.email-removed',
}

export default {
  AlertSchemes,
  BookingCalendarView,
  BookingsTableColumns,
  BookingsTableFilterOptions,
  BookingStatus,
  BookingsViews,
  BookingsViewTypes,
  CalendarManagementType,
  CalendarProviders,
  ColorSchemes,
  dateFormatStrings,
  DateFormatStrings,
  defaultSlotDuration,
  EventLocationType,
  ExternalConnectionProviders,
  ftueStep,
  InviteStatus,
  locationTypes,
  loginRedirectKey,
  meetingLinkProviderType,
  MetricEvents,
  ModalStates,
  ScheduleCreationState,
  SettingsSections,
  SubscriberLevels,
  TableDataButtonType,
  TableDataType,
  tooltipPosition,
  WaitingListAction,
};

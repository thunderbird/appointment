/**
 * Possible values for VITE_AUTH_SCHEME
 */
export enum AuthSchemes {
  Password = 'password',
  Fxa = 'fxa',
  Oidc = 'oidc',
}

/**
 * Available date format strings
 */
export enum DateFormatStrings {
  // Qalendar specific formats (These have to be in this format for qalendar to understand them)
  // TODO: remove Qalendar specific enums
  Qalendar = 'YYYY-MM-DD HH:mm',
  QalendarFullDay = 'YYYY-MM-DD',
  // Time display formats
  Display12Hour = 'hh:mma',
  Display24Hour = 'HH:mm',
  // Other formats
  UniqueMonth = 'YYYY-MM',
}

/**
 * Defined durations in minutes for scheduled time slots
 */
export const SLOT_DURATION_OPTIONS = [15, 30, 45, 60, 75, 90];

/**
 * The amount of time in minutes a schedule's slot duration will default to
 * Must be a value from SLOT_DURATION_OPTIONS
 */
export const DEFAULT_SLOT_DURATION = 30;

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
  Declined = 4,
  Cancelled = 5,
  Modified = 6
}

export enum BookingsFilterOptions {
  All = 'all',
  Unconfirmed = 'unconfirmed'
}

export enum BookingsSortOptions {
  DateRequested = 'date-requested',
  MeetingDate = 'meeting-date'
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
  AccountSettings = 1,
  Preferences = 2,
  ConnectedApplications = 3,
}

/**
 * Available color schemes for theme
 */
export enum ColourSchemes {
  System = 'system',
  Dark = 'dark',
  Light = 'light',
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
  Caldav = 4,
  _DEPRECATED = 5,
  Oidc = 6,
}

/**
 * Meeting provider types (matches the backends version)
 */
export enum MeetingLinkProviderType {
  None = 'none',
  Zoom = 'zoom',
  GoogleMeet = 'google_meet',
}

/**
 * Alert levels
 */
export enum AlertSchemes {
  Error = 1, // Alert indicates something's gone wrong
  Warning = 2, // Alert indicates something important
  Success = 3, // Alert indicates something's gone right
  Info = 4, // Alert indicates some neutral information
}

/**
 * Used as the session storage key for the location the user wanted to go to before logging in.
 */
export const LOGIN_REDIRECT_KEY = 'loginRedirect';

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
 */
export enum FtueStep {
  ConnectCalendars = 20,
  ConnectCalendarsCalDav = 21,
  ConnectCalendarsGoogle = 22,
  CreateBookingPage = 30,
  SetAvailability = 40,
  VideoMeetingLink = 50,
  SetupComplete = 100,
}

export enum TooltipPosition {
  None = 'pos-none',
  Top = 'pos-top',
  Bottom = 'pos-bottom',
  Left = 'pos-left',
  Right = 'pos-right',
}

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
  CancelBooking = 'apmt.booking.cancel',
  ModifyBooking = 'apmt.booking.modify',
  ConfirmBooking = 'apmt.booking.confirm',
  DenyBooking = 'apmt.booking.deny',
  RequestBooking = 'apmt.booking.request',
  ScheduleCreated = 'apmt.schedule.created',
  ScheduleUpdated = 'apmt.schedule.updated',
  SignUp = 'apmt.signup',
  SignUpAlreadyExists = 'apmt.signup.already-exists',
  Login = 'apmt.login',
}

export const ProviderDisplayName: Record<string, string> = {
  caldav: 'CalDAV',
  google: 'Google',
  zoom: 'Zoom',
};

export default {
  AlertSchemes,
  AuthSchemes,
  BookingCalendarView,
  BookingStatus,
  CalendarProviders,
  ColourSchemes,
  DateFormatStrings,
  DEFAULT_SLOT_DURATION,
  EventLocationType,
  ExternalConnectionProviders,
  FtueStep,
  LOGIN_REDIRECT_KEY,
  MeetingLinkProviderType,
  MetricEvents,
  ProviderDisplayName,
  SettingsSections,
  SLOT_DURATION_OPTIONS,
  TableDataButtonType,
  TableDataType,
  TooltipPosition,
};

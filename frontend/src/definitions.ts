/**
 * Possible values for VITE_AUTH_SCHEME
 */
export enum AuthSchemes {
  Password = 'password',
  Fxa = 'fxa',
  Accounts = 'accounts'
}

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
 * Appointment subscriber levels
 */
export enum SubscriberLevels {
  Basic = 1,
  Plus = 2,
  Pro = 3,
  Admin = 99,
}

/**
 * Schedule creation state
 */
export enum ScheduleCreationState {
  Availability = 1,
  Settings = 2,
  Details = 3,
  Booking = 4,
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
export enum ColourSchemes {
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
  Caldav = 4,
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
  SetupProfile = 10,
  CalendarProvider = 20,
  ConnectCalendars = 30,
  SetupSchedule = 40,
  ConnectVideoConferencing = 50,
  Finish = 100,
}

export enum TooltipPosition {
  None = 'pos-none',
  Top = 'pos-top',
  Bottom = 'pos-bottom',
  Left = 'pos-left',
  Right = 'pos-right',
}

/**
 * This should match the enum in routes/waiting_list.py
 */
export enum WaitingListAction {
  Confirm = 1,
  Leave = 2,
}

/**
 * Colors used for solor select inputs
 */
export enum ColorPalette {
  Rose = '#ff7b91',
  Pink = '#fe64b6',
  Fuchsia = '#c276c5',
  Purple = '#b865ff',
  Blue = '#8fa5ff',
  Sky = '#64c2d0',
  Teal = '#64bead',
  Green = '#73c690',
  Orange = '#e0ad6a',
  Red = '#ff8b67',
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

export enum Dismissibles {
  BetaWarning = 'beta-warning'
}

export default {
  AlertSchemes,
  AuthSchemes,
  BookingCalendarView,
  BookingsTableColumns,
  BookingsTableFilterOptions,
  BookingStatus,
  BookingsViews,
  BookingsViewTypes,
  CalendarManagementType,
  CalendarProviders,
  ColorPalette,
  ColourSchemes,
  DateFormatStrings,
  DEFAULT_SLOT_DURATION,
  Dismissibles,
  EventLocationType,
  ExternalConnectionProviders,
  FtueStep,
  InviteStatus,
  LOGIN_REDIRECT_KEY,
  MeetingLinkProviderType,
  MetricEvents,
  ModalStates,
  ScheduleCreationState,
  SettingsSections,
  SLOT_DURATION_OPTIONS,
  SubscriberLevels,
  TableDataButtonType,
  TableDataType,
  TooltipPosition,
  WaitingListAction,
};

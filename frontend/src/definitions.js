// appointment location types
export const subscriberLevels = {
  basic: 1,
  plus: 2,
  pro: 3,
  admin: 99,
};

// appointment location types
export const locationTypes = {
  inPerson: 1,
  online: 2,
};

// appointment creation state
export const appointmentCreationState = {
  hidden: 0,
  details: 1,
  availability: 2,
  finished: 3,
};

// schedule creation state
export const scheduleCreationState = {
  details: 1,
  availability: 2,
  settings: 3,
};

// available calendar views
export const calendarViews = {
  day: 1,
  week: 2,
  month: 3,
};

// extended calendar views for booking
export const bookingCalendarViews = {
  ...calendarViews,
  weekAfterMonth: 4,
  loading: 10,
  success: 11,
  invalid: 12,
};

// available appointment views
export const appointmentState = {
  booked: 1,
  pending: 2,
  past: 3,
};

// available appointment views
export const appointmentViews = {
  ...appointmentState,
  all: 4,
};

// columns for appointments list view
export const listColumns = {
  title: 1,
  status: 2,
  active: 3,
  calendar: 4,
  bookingLink: 5,
  replies: 6,
};

// appointments list filter options
export const filterOptions = {
  allAppointments: 1,
  appointmentsToday: 2,
  appointmentsNext7Days: 3,
  appointmentsNext14Days: 4,
  appointmentsNext31Days: 5,
  appointmentsInMonth: 6,
  allFutureAppointments: 7,
};

// data view types
export const viewTypes = {
  list: 1,
  grid: 2,
};

// sections on settings page
// TODO: enable implemented sections
export const settingsSections = {
  general: 1,
  calendar: 2,
  // appointmentsAndBooking: 3,
  account: 4,
  // privacy:                5,
  // faq:                    6,
};

// available color schemes for theme
export const colorSchemes = {
  system: 1,
  dark: 2,
  light: 3,
};

export const calendarManagementType = {
  connect: 1,
  edit: 2,
};

export const meetingLinkProviderType = {
  none: 0,
  zoom: 1,
  google_meet: 2,
};

export default {
  subscriberLevels,
  appointmentState,
  appointmentViews,
  bookingCalendarViews,
  calendarViews,
  colorSchemes,
  appointmentCreationState,
  scheduleCreationState,
  filterOptions,
  listColumns,
  locationTypes,
  settingsSections,
  viewTypes,
  meetingLinkProviderType,
};

// appointment location types
export const locationTypes = {
  inPerson: 1,
  online:   2,
};

// appointment creation state
export const creationState = {
  hidden:       0,
  details:      1,
  availability: 2,
  finished:     3,
}

// available calendar views
export const calendarViews = {
  day:   1,
  week:  2,
  month: 3,
};

// extended calendar views for booking
export const bookingCalendarViews = {
  ...calendarViews,
  weekAfterMonth: 4,
};

// available appointment views
export const appointmentState = {
  booked:  1,
  pending: 2,
  past:    3,
};

// available appointment views
export const appointmentViews = {
  ...appointmentState,
  all: 4,
};

// columns for appointments list view
export const listColumns = {
  title:       1,
  status:      2,
  active:      3,
  calendar:    4,
  bookingLink: 5,
  replies:     6,
};

// appointments list filter options
export const filterOptions = {
  allAppointments:        1,
  appointmentsToday:      2,
  appointmentsNext7Days:  3,
  appointmentsNext14Days: 4,
  appointmentsNext31Days: 5,
  appointmentsInMonth:    6,
  allFutureAppointments:  7,
};

// data view types
export const viewTypes = {
  list: 1,
  grid: 2,
};

// settingsSections
export const settingsSections = {
  general:                1,
  calendar:               2,
  appointmentsAndBooking: 3,
  account:                4,
  privacy:                5,
  faq:                    6,
};

export default {
  locationTypes,
  creationState,
  calendarViews,
  bookingCalendarViews,
  appointmentState,
  appointmentViews,
  listColumns,
  filterOptions,
  viewTypes,
  settingsSections,
}

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
	settingsSections
}

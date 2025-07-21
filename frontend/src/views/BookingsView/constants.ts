import { BookingStatus, BookingStatusFilterQueryParams } from '@/definitions'

export const BOOKING_STATUS_TO_FILTER_QUERY_PARAM = {
  [BookingStatus.Requested]: BookingStatusFilterQueryParams.Requested,
  [BookingStatus.Booked]: BookingStatusFilterQueryParams.Booked,
  [BookingStatus.Declined]: BookingStatusFilterQueryParams.Declined,
  [BookingStatus.Cancelled]: BookingStatusFilterQueryParams.Cancelled,
}

export const FILTER_QUERY_PARAM_TO_BOOKING_STATUS = {
  [BookingStatusFilterQueryParams.Requested]: BookingStatus.Requested,
  [BookingStatusFilterQueryParams.Booked]: BookingStatus.Booked,
  [BookingStatusFilterQueryParams.Declined]: BookingStatus.Declined,
  [BookingStatusFilterQueryParams.Cancelled]: BookingStatus.Cancelled,
}

export enum APPOINTMENT_SLIDING_PANEL_STEPS {
  DETAILS,
  CONFIRMATION,
  MODIFY,
  CANCEL
}

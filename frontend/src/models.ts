import { Dayjs } from "dayjs";

export type Attendee = {
  id: number;
  email: string;
  name: string;
  timezone: string;
}

export type Slot = {
  id: number;
  start: Dayjs;
  duration: number;
  attendee_id: number;
  booking_tkn: string;
  booking_expires_at: string;
  booking_status: number;
  meeting_link_id: number;
  meeting_link_url: string;
  appointment_id: number;
  subscriber_id: number;
  time_updated: string;
  attendee: Attendee;
}

export type Appointment = {
  id: number;
  title: string;
  details: string;
  slug: string;
  location_url: string;
  calendar_id: number;
  duration: number;
  location_type: number;
  location_suggestions: string;
  location_selected: number;
  location_name: string;
  location_phone: string;
  keep_open: boolean;
  status: number;
  meeting_link_provider: string;
  uuid: string;
  time_created: string;
  time_updated: string;
  slots: Slot[];
  calendar_title: string;
  calendar_color: string;
  active: boolean;
};

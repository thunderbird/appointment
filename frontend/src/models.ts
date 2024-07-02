import { Dayjs } from "dayjs";
import { UseFetchReturn } from '@vueuse/core';

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

export type Calendar = {
  id?: number;
  connected: boolean;
  title: string;
  color: string;
};

export type ExternalConnection = {
  owner_id: number;
  name: string;
  type: string;
  type_id: string;
};

export type ExternalConnectionCollection = {
  fxa?: ExternalConnection[];
  google?: ExternalConnection[];
  zoom?: ExternalConnection[];
};

// This will be used later if we provide custom availabilities
// in addition to general availability too
export type Availability = {
  id?: number;
};

export type Schedule = {
  active: boolean;
  name: string;
  slug: string;
  calendar_id: number;
  location_type: number;
  location_url: string;
  details: string;
  start_date: string;
  end_date: string;
  start_time: string;
  end_time: string;
  earliest_booking: number;
  farthest_booking: number;
  weekdays: number[];
  slot_duration: number;
  meeting_link_provider: string;
  id: number;
  time_created: string;
  time_updated: string;
  availabilities?: Availability[];
  calendar: Calendar;
};

export type User = {
  email: string;
  preferredEmail: string;
  level: number;
  name: string;
  timezone: string;
  username: string;
  signedUrl: string;
  avatarUrl: string;
  accessToken: string;
  scheduleSlugs: string[];
}

export type Subscriber = {
  username: string;
  name: string;
  email: string;
  preferred_email: string;
  level: number;
  timezone: string;
  avatar_url: string;
}

export type Signature = {
  url: string;
}

// Types and aliases used for our custom createFetch API calls and return types
export type Fetch = (url: string) => UseFetchReturn<any> & PromiseLike<UseFetchReturn<any>>;
export type BooleanResponse = UseFetchReturn<boolean>;
export type SignatureResponse = UseFetchReturn<Signature>;
export type SubscriberResponse = UseFetchReturn<Subscriber>;
export type TokenResponse = UseFetchReturn<Token>;
export type AppointmentListResponse = UseFetchReturn<Appointment[]>;
export type CalendarListResponse = UseFetchReturn<Calendar[]>;
export type ScheduleListResponse = UseFetchReturn<Schedule[]>;
export type ExternalConnectionCollectionResponse = UseFetchReturn<ExternalConnectionCollection>;

export type Error = { error: boolean|string|null };
export type Token = {
  access_token: string;
  token_type: string;
}

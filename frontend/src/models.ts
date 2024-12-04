import { Dayjs } from 'dayjs';
import { UseFetchReturn } from '@vueuse/core';
import {
  InviteStatus,
  WaitingListAction,
  EventLocationType,
  FtueStep,
  CalendarProviders,
  TableDataButtonType,
  TableDataType,
} from './definitions';

export type Attendee = {
  id?: number;
  email: string;
  name: string;
  timezone: string;
};

export type Slot = {
  id: number;
  start: Dayjs|string;
  duration: number;
  attendee_id: number;
  booking_tkn?: string;
  booking_expires_at?: string;
  booking_status?: number;
  meeting_link_id?: number;
  meeting_link_url?: string;
  appointment_id?: number;
  subscriber_id?: number;
  time_updated?: string;
  attendee?: Attendee;
  selected?: boolean;
};

export type SlotAttendee = {
  slot: Slot;
  attendee: Attendee;
};

export type Appointment = {
  id: number;
  title: string;
  details: string;
  slug: string;
  location_url: string;
  calendar_id: number;
  duration: number;
  location_type: number; // TODO
  location_suggestions: string;
  location_selected: number;
  location_name: string;
  location_phone: string;
  keep_open: boolean;
  status: number; // TODO
  meeting_link_provider: string;
  uuid: string;
  time_created: string;
  time_updated: string;
  slots: Slot[];
  calendar_title: string;
  calendar_color: string;
  active: boolean;
  owner_name?: string;
  slot_duration?: number;
  booking_confirmation?: boolean;
};

/**
 * Appointment with slots from current schedule data
 */
export type ScheduleAppointment = {
  title: string;
  calendar_id: number;
  calendar_title: string;
  location_type: number; // TODO
  location_url: string;
  details: string;
  status: number; // TODO
  slots: Slot[];
  type: string; // TODO
};

export type CustomEventData = {
  attendee?: Attendee;
  slot_status: number; // TODO: definitions.BookingStatus?
  booking_status: number; // TODO: definitions.BookingStatus
  calendar_title: string;
  calendar_color: string;
  duration: number;
  preview: boolean;
  all_day: boolean;
  remote: boolean;
  tentative: boolean;
};

export type CalendarEvent = {
  id: number|string;
  title: string;
  colourScheme: string;
  time?: TimeFormatted;
  description: string;
  with: string;
  customData: CustomEventData;
  isCustom?: boolean;
};

/**
 * Event location.
 * Corresponds to schemas.EventLocation
 */
export type EventLocation = {
  type: EventLocationType;
  suggestions?: string;
  selected?: string;
  name?: string;
  url?: string;
  phone?: string;
};

/**
 * Event from a remote calendar.
 * Corresponds to schemas.Event
 */
export type RemoteEvent = {
  title: string;
  start: string;
  end: string;
  all_day?: boolean;
  tentative?: boolean;
  description?: string;
  calendar_title?: string;
  calendar_color?: string;
  location?: EventLocation;
  uuid?: string;
  duration?: number;
};

export type EventPopup = {
  event?: CalendarEvent;
  display: string;
  top: string|number;
  left: string|number;
  right?: string|number;
  bottom?: string|number;
};

export type Calendar = {
  id?: number;
  connected: boolean;
  title: string;
  color: string;
  provider?: CalendarProviders;
  url?: string;
  user?: string;
};

export type CalendarItem = {
  key: number;
  label: string;
  checked: boolean;
};

export type ExternalConnection = {
  owner_id: number;
  name: string;
  type: string;
  type_id: string;
};

export type ExternalConnectionCollection = {
  accounts?: ExternalConnection[];
  fxa?: ExternalConnection[];
  google?: ExternalConnection[];
  zoom?: ExternalConnection[];
  caldav?: ExternalConnection[];
};

// The type `Availability` will be used later if we provide custom availabilities
// in addition to general availability too
export type Availability = {
  id?: number;
};

export type Schedule = {
  active: boolean;
  name: string;
  slug?: string;
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
  id?: number;
  time_created?: string;
  time_updated?: string;
  availabilities?: Availability[];
  calendar?: Calendar;
  booking_confirmation: boolean;
};

export type Invite = {
  subscriber_id?: number;
  code: string;
  status: InviteStatus;
  time_created: string;
  time_updated: string;
};

export type User = {
  email: string;
  preferredEmail: string;
  level: number;
  name: string;
  settings: UserConfig;
  username: string;
  signedUrl: string;
  avatarUrl: string;
  accessToken: string;
  scheduleLinks: string[];
  isSetup: boolean,
  uniqueHash: string;
};

/**
 * User settings to customize the application
 * Used to store language, theme, time format and such.
 */
export type UserConfig = {
  language: string,
  colourScheme: string,
  timeFormat: number,
  timezone: string;
};

/**
 * User activity as in the things they do within our application
 * Used to store the state of dismissables and such.
 */
export type UserActivity = {
  dismissedBetaWarning: boolean,
};

export type Subscriber = {
  id?: number;
  username: string;
  name?: string;
  email?: string;
  preferred_email?: string;
  level?: number;
  language?: string;
  timezone?: string;
  colour_scheme?: string;
  time_mode?: number;
  avatar_url?: string;
  is_setup?: boolean;
  unique_hash?: string;
  schedule_links?: string[];
  secondary_email?: string;
  invite?: Invite;
  time_created?: string;
  time_deleted?: string;
}

export type WaitingListInvite = {
  accepted: number[];
  errors: string[]
}

export type WaitingListEntry = {
  id: number;
  email: string;
  email_verified: boolean;
  invite_id?: number;
  invite?: Invite;
  time_created?: string;
  time_updated?: string;
}

export type WaitingListStatus = {
  action: WaitingListAction;
  success: boolean;
  redirectToSettings?: boolean;
}

export type Signature = {
  url: string;
};

// Types for authentication, messages and error handling
export type Alert = {
  title: string;
  details?: string;
};
export type Error = {
  error: boolean|string|null;
  message?: string;
};
export type ExceptionDetail = {
  id?: string;
  message?: string;
  status?: number;
}
export type PydanticExceptionDetail = {
  ctx: { reason: string, ge?: string },
  input: string,
  loc: string[],
  msg: string,
  type: string
}
export type FormExceptionDetail = {
  id: string,
  message: string,
  reason: string,
  status: number
}
export type PydanticException = {
  detail?: string|FormExceptionDetail|PydanticExceptionDetail[];
}
export type Exception = {
  status_code?: number;
  detail?: ExceptionDetail | PydanticExceptionDetail[];
  headers?: any[];
};
export type Token = {
  access_token: string;
  token_type: string;
};
export type AuthUrl = {
  url: string;
};
export type PageMeta = {
  page: number,
  total_pages: number
  per_page: number,
  count: number,
}

// Types and aliases used for our custom createFetch API calls and return types
export type AuthUrlResponse = UseFetchReturn<AuthUrl|Exception>;
export type AppointmentListResponse = UseFetchReturn<Appointment[]>;
export type AppointmentResponse = UseFetchReturn<Appointment>;
export type AvailabilitySlotResponse = UseFetchReturn<SlotAttendee>;
export type BooleanResponse = UseFetchReturn<boolean|Exception>;
export type BlobResponse = UseFetchReturn<Blob>;
export type CalendarResponse = UseFetchReturn<Calendar|Exception>;
export type CalendarListResponse = UseFetchReturn<Calendar[]>;
export type ExternalConnectionCollectionResponse = UseFetchReturn<ExternalConnectionCollection>;
export type Fetch = (url: string) => UseFetchReturn<any> & PromiseLike<UseFetchReturn<any>>;
export type InviteListResponse = UseFetchReturn<Invite[]|Exception>;
export type Refresh = () => Promise<void>;
export type RemoteEventListResponse = UseFetchReturn<RemoteEvent[]>;
export type ScheduleResponse = UseFetchReturn<Schedule|Exception>;
export type ScheduleListResponse = UseFetchReturn<Schedule[]>;
export type SignatureResponse = UseFetchReturn<Signature>;
export type SlotResponse = UseFetchReturn<Slot|Exception>;
export type StringResponse = UseFetchReturn<string|Exception>;
export type StringListResponse = UseFetchReturn<string[]>;
export type SubscriberResponse = UseFetchReturn<Subscriber>;
export type TokenResponse = UseFetchReturn<Token>;
export type WaitingListInviteResponse = UseFetchReturn<WaitingListInvite|Exception>
export type WaitingListResponse = UseFetchReturn<WaitingListEntry[]|Exception>;
export type WaitingListActionResponse = UseFetchReturn<WaitingListStatus>;
export type ListResponse = UseFetchReturn<{
  page_meta: PageMeta,
  items: any[]
}>;

// Table types
export type TableDataField = {
  type: TableDataType;
  value: string|number|boolean;
  link?: string;
  buttonType?: TableDataButtonType;
  disabled?: boolean;
  tooltip?: string;
};
export type TableDataRow = {
  [key:string]: TableDataField
};
export type TableDataColumn = {
  name: string;
  key: string;
};
export type TableFilterOption = {
  name: string;
  key: string;
};
export type TableFilter = {
  name: string;
  options: TableFilterOption[];
  fn: (value: string, list: TableDataRow[]) => TableDataRow[];
};

// First Time User Experience State
export type FtueState = {
  previous: FtueStep;
  next: FtueStep;
  title: string;
};

// Utility types
export type Time<T> = {
  start: T;
  end: T;
};
export type TimeNumeric = Time<number>;
export type TimeFormatted = Time<string>;

export type SelectOption = {
  label: string;
  value: number;
};

export type Coloring = {
  border?: string;
  background?: string;
};

export type HTMLElementEvent = Event & {
  target: HTMLElement;
  currentTarget: HTMLElement;
};
export type HTMLInputElementEvent = Event & {
  target: HTMLInputElement;
  currentTarget: HTMLInputElement;
};

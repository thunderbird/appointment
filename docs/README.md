# Documentation Thunderbird Appointment

This place holds all additional technical documentation for Thunderbird Appointment.

## API endpoints

After starting the backend container, you can find the API documentation here: <http://localhost:8090/docs>

## Project architecture

This are the general components, Thunderbird Appointment consists of.

```mermaid
C4Component

  ContainerDb(c4, "Database", "MySQL", "Subscribers, calendars,<br>appointments, attendees, ...")
  Container(c1, "Frontend", "Vue3 / Tailwind", "Provides all Appointment<br>functionality to customers<br>via their web browser")
  Container_Boundary(b1, "Backend") {
    Component(c3, "Subscriber Area", "FastAPI, JWT auth", "Provides functionality related<br>to calendar connections,<br>appointments, general availability")
    Component(c2, "Auth Controller", "FastAPI", "Redirects to FxA service,<br>authenticates subscriber,<br>gets subscription level")
    Component(c5, "Public Link Area", "FastAPI", "Allows visitors to choose<br>slots in given<br>availability timeline.")
    Boundary(e1, "External Connections") {
      System_Ext(e3, "Google", "Allows to query and write<br>event data into calendars<br>using Google API")
      System_Ext(e2, "CalDAV", "Allows to query and write<br>event data into calendars<br>using CalDAV format")
      System_Ext(e1, "FxA", "Allows users to register,<br>sign in and subscribe<br>to an Appointment tier")
      System_Ext(e4, "Zoom", "Allows to create meeting links<br>and attach them to events<br>using Zoom integration")
    }
  }
  BiRel(c1, c2, "Call Sign up / in", "HTTPS")
  Rel(c2, c3, "Authentication<br>succeeded", "Session")
  BiRel(c3, c4, "Query data, migrate data", "SQLAlchemy, Alembic")
  Rel(c1, c5, "Public Link Call", "HTTPS")
  BiRel(c2, e1, "Authenticate Account", "OAuth2")
  BiRel(c3, e2, "Query event data", "JSON/HTTPS")
  BiRel(c3, e3, "Query event data", "JSON/HTTPS")
  BiRel(c3, e4, "Meeting links", "JSON/HTTPS")

  UpdateRelStyle(c1, c2, $textColor="#999", $offsetY="-60", $offsetX="-110")
  UpdateRelStyle(c2, c3, $textColor="#999", $offsetY="20", $offsetX="-38")
  UpdateRelStyle(c3, c4, $textColor="#999", $offsetY="-50", $offsetX="10")
  UpdateRelStyle(c1, c5, $textColor="#999", $offsetY="-60", $offsetX="-60")
  UpdateRelStyle(c2, e1, $textColor="#999", $offsetY="0", $offsetX="10")
  UpdateRelStyle(c3, e2, $textColor="#999", $offsetY="0", $offsetX="10")
  UpdateRelStyle(c3, e3, $textColor="#999", $offsetY="0", $offsetX="10")
  UpdateRelStyle(c3, e4, $textColor="#999", $offsetY="150", $offsetX="20")
  UpdateElementStyle(c4, $fontColor="black", $bgColor="#eddcea", $borderColor="#a30086")
  UpdateElementStyle(c2, $bgColor="#456789")
  UpdateElementStyle(c3, $bgColor="#456789")
  UpdateElementStyle(c5, $bgColor="#456789")
  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Entity relations

The database contains the following tables and columns.

```mermaid
erDiagram
  ALEMBIC_VERSION {
    string version_num PK "Unique hash indicating current db migration state"
  }
  SUBSCRIBERS {
    int id PK "Unique user key"
    string username "URL-friendly username, format is restricted"
    string email "Preferred email address (synced with FxA)"
    string name "Preferred display name"
    enum level "Subscription level [basic, plus, pro, admin]"
    int timezone "User selected home timezone, UTC offset"
    string avatar_url "Public link to an avatar image"
    string short_link_hash "Hash for verifying user link"
    string minimum_valid_iat_time "Minimum valid issued at time timestamp"
    date time_created "UTC timestamp of subscriber creation"
    date time_updated "UTC timestamp of last subscriber modification"
    string secondary_email "Secondary email address"
    date time_deleted "UTC timestamp of deletion (soft delete)"
    int ftue_level "Progress on first time user experience flow"
  }
  SUBSCRIBERS ||--o{ CALENDARS : own
  CALENDARS {
    int id PK "Unique calendar key"
    int owner_id FK "Person who owns this calendar"
    enum provider "Calendar provider [Google, CalDAV]"
    string title "Calendar title to identify connection in lists"
    string color "Color to visually identify calendars"
    string url "CalDAV url of remote calendar"
    string user "Username to access the calendar"
    string password "Passphrase to access the calendar"
    bool connected "Flag indicating if calendar is actively used"
    date connected_at "Date calendar was connected"
    date time_created "UTC timestamp of calendar creation"
    date time_updated "UTC timestamp of last calendar modification"
  }
  SUBSCRIBERS ||--o{ EXTERNAL_CONNECTIONS : create
  EXTERNAL_CONNECTIONS {
    int id PK "Unique connection key"
    int owner_id FK "Person who creates and owns this connection"
    string name "Custom connection title"
    enum type "Connection type [zoom, google, fxa, caldav]"
    string type_id "Universal unique identifier"
    string token "Passphrase or passtoken for connecting"
    date time_created "UTC timestamp of connection creation"
    date time_updated "UTC timestamp of last connection modification"
  }
  SUBSCRIBERS ||--o{ INVITES : hold
  INVITES {
    int id PK "Unique invite key"
    int subscriber_id FK "Person who holds this invite"
    string code "Unique invitation code"
    enum status "Invitation status [active, revoked]"
    date time_created "UTC timestamp of invite creation"
    date time_updated "UTC timestamp of last invite modification"
    int owner_id FK "Person who creates and owns this invite"
  }
  INVITES ||--o{ WAITING_LIST : manage
  WAITING_LIST {
    int id PK "Unique waiting list entry key"
    string email "Email address invited"
    date email_verified "UTC timestamp of email verification"
    int invite_id FK "Invited associated with this waiting list entry"
    date time_created "UTC timestamp of waiting list entry creation"
    date time_updated "UTC timestamp of last waiting list entry modification"
  }
  CALENDARS ||--o{ APPOINTMENTS : create_from
  APPOINTMENTS {
    int id PK "Unique appointment key"
    int calendar_id FK "Calendar connected to the appointment"
    date time_created "UTC timestamp of appointment creation"
    date time_updated "UTC timestamp of last appointment modification"
    int duration "Appointment default duration, number of minutes [10-600]"
    string title "Short appointment title"
    enum location_type "[In person, online]"
    string location_suggestions "Semicolon separated predefined location keys (teams, zoom, jitsy, phone call etc.)"
    int location_selected "Key of final location selected from suggestions by appointment creator"
    string location_name "Custom location title"
    string location_url "URL the appointment is held at"
    string location_phone "Phone number the appointment is held at"
    string details "Detailed appointment description or agenda"
    string slug "Generated random string to build share links for the appointment"
    bool keep_open "If true appointment accepts selection of multiple slots (future feature)"
    enum status "Appointment state [draft, ready, close]"
    string meeting_link_provider "Name of the provider for meeting links (e.g. Zoom)"
    uuid uuid "Binary field holding a universal unique identifier"
  }
  CALENDARS ||--|{ SCHEDULES : connected_to
  SCHEDULES {
    int id PK "Unique schedule key"
    int calendar_id FK "Calendar which events are created in for this schedule"
    bool active "True if schedule is enabled"
    string name "Schedule title"
    enum location_type "[In person, online]"
    string location_url "URL events are held at"
    string details "Detailed event description or agenda"
    date start_date "UTC start date of scheduled date range"
    date end_date "UTC end date of scheduled date range"
    date start_time "UTC start time on selected weekdays"
    date end_time "UTC end time on selected weekdays"
    int earliest_booking "Can't book if it's less than this many minutes before start time"
    int farthest_booking "Can't book if start time is more than this many minutes away"
    json weekdays "List of selected weekdays (1-7, ISO format)"
    int slot_duration "Size of the Slot that can be booked in minutes"
    date time_created "UTC timestamp of schedule creation"
    date time_updated "UTC timestamp of last schedule modification"
    string meeting_link_provider "Name of the provider for meeting links (e.g. Zoom)"
    string slug "Random or customized url part"
    bool booking_confirmation "True if booking requests need to be confirmed by owner"
    string timezone "Configured timezone name"
  }
  SCHEDULES ||--|{ AVAILABILITIES : hold_custom
  SCHEDULES ||--|{ SLOTS : provide_on_request
  AVAILABILITIES {
    int id PK "Unique availability key"
    int schedule_id FK "Schedule this availability is for"
    string day_of_week "Day of week the times are chosen for"
    date start_time "UTC timestamp of availbale start time"
    date end_time "UTC timestamp of available end time"
    string min_time_before_meeting "Can't book if it's less than this many minutes before start time"
    int slot_duration "Size of the Slot that can be booked in minutes"
    date time_created "UTC timestamp of schedule creation"
    date time_updated "UTC timestamp of last schedule modification"
  }
  APPOINTMENTS ||--|{ SLOTS : provide_manual_selected
  SLOTS {
    int id PK "Unique key of available time slot"
    int appointment_id FK "Appointment this slot was provided for"
    int schedule_id FK "Schedule this slot was requested for"
    int attendee_id FK "Attendee who selected this slot"
    int subscriber_id FK "Subscriber who chose this slot"
    date time_updated "UTC timestamp of last slot modification"
    date start "UTC timestamp of slot starting time"
    int duration "Custom slot duration, number of minutes [10-600]"
    string meeting_link_id "Meeting link identifier"
    string meeting_link_url "Meeting link url"
    string booking_tkn "Temp storage for verifying booking slot"
    date booking_expires_at "Booking expiration date"
    enum booking_status "[none, requested, booked]"
    date time_created "UTC timestamp of slot creation"
  }
  SUBSCRIBERS ||--o{ SLOTS : choose
  ATTENDEES ||--o{ SLOTS : select
  ATTENDEES {
    int id PK "Unique key of attendee"
    string email "Email address of the attendee"
    string name "Name of the attendee"
    date time_created "UTC timestamp of attendee creation"
    date time_updated "UTC timestamp of last attendee modification"
    string timezone "Detected timezone name"
  }
```

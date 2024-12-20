### Thunderbird Appointment Backend Strings

# Locale code
locale = en

# Format Strings

# Time Format: 8:23pm
time-format = %I:%M%p
# Date Format: Sunday, April 04, 2024
date-format = %A, %B %d, %Y

## Health Check

# Should indicate application wellness.
health-ok = Health OK
health-bad = Health BAD

## General Exceptions

unknown-error = An unknown error occurred. Please try again later.
unknown-error-short = an unknown error

appointment-not-found = The appointment could not be found.
calendar-not-found = The calendar could not be found.
schedule-not-found = The schedule could not be found.
slot-not-found = The time slot you have selected could not be found. Please try again.
subscriber-not-found = The subscriber could not be found.

appointment-not-auth = You are not authorized to view or modify this appointment.
calendar-not-auth = You are not authorized to view or modify this calendar.
schedule-not-auth = You are not authorized to view or modify this schedule.
slot-not-auth = You are not authorized to view or modify this time slot.

account-delete-fail = There was a problem deleting your data. This incident has been logged and your data will manually be removed.
protected-route-fail = No valid authentication credentials provided.
username-not-available = This username has already been taken.
invalid-link = This link is no longer valid.
calendar-sync-fail = An error occurred while syncing calendars. Please try again later.
calendar-not-active = The calendar connection is not active.
slot-not-found = There are no available time slots to book.
slot-already-taken = The time slot you have selected is no longer available. Please try again.
slot-invalid-email = The email you have provided was not valid. Please try again.
invite-code-not-valid = The invite code you used is not valid.
not-in-allow-list = Your email is not in the allow list.

schedule-not-active = The schedule has been turned off. Please contact the schedule owner for more information.

remote-calendar-connection-error = The remote calendar could not be reached due to {$reason}.

        Please verify your connection information and try again.

# Possible entries for $reason,
remote-calendar-reason-doesnt-support-caldav = the remote calendar does not support CalDAV
remote-calendar-reason-doesnt-support-auth = the remote calendar does not support authentication
remote-calendar-reason-unauthorized = an issue with your username or password

event-could-not-be-accepted = There was an error accepting the booking details. Please try again later.
event-could-not-be-deleted = There was an error removing the hold event. Please try again later.

failed-to-create-subscriber = There was an error creating the subscriber. Please try again later.
subscriber-already-exists = A subscriber with this email address already exists.
subscriber-already-deleted = The subscriber is already deleted.
subscriber-already-enabled = The subscriber is already enabled.
subscriber-self-delete = You are not allowed to delete yourself here.

rate-limit-exceeded = Too many requests in a short period. Please try again later.

# This is for the frontend, don't variable-ify!
error-minimum-value = {field} should be at least {value}.

## Authentication Exceptions

email-mismatch = Email mismatch.
invalid-credentials = The provided credentials are not valid.
disabled-account = Your account has been disabled.
oauth-error = There was an error with the authentication flow. Please try again.

## Zoom Exceptions

zoom-not-connected = You need a connected Zoom account in order to create a meeting link.
zoom-connect-to-continue = You must connect a Zoom account, enter a custom meeting link, or click "Skip Connect Video" to continue.

## Google Exceptions

google-connection-error = Error connecting with Google API, please re-connect.
google-scope-changed = You must enable Calendar and Event access to use Thunderbird Appointment.
google-invalid-creds = Google authentication credentials are not valid.
google-auth-fail = Google authentication failed.
google-auth-expired = Google authentication session expired, please try again.
google-sync-fail = An error occurred while syncing calendars. Please try again later.
google-only-one = You can only have one Google account connected.
google-connect-to-continue = You must connect at least one Google account to continue.

## Frontend Facing Strings

event-title-template = { $prefix }Appointment - { $name1 } and { $name2 }
event-hold-prefix = HOLD:
# If the calendar event does not have a title this will be used instead
event-summary-default = Untitled Event

## Event File Strings

# Variables:
# $url (String) - A link to the external meeting room for the meeting (e.g. Zoom meeting, Google Meets, Matrix chatroom, etc..)
join-online = Join online at: { $url }

# Variables:
# $phone (String) - An unformatted phone number for the meeting
join-phone = Join by phone: { $phone }

# Waiting List Errors
wl-subscriber-already-exists = { $email } is already a subscriber...that's weird!
wl-subscriber-failed-to-create = { $email } was unable to be invited. Please make a bug report!

## Account Data Readme

# This is a text file that is generated and bundled along with your account data
# Variables:
# $download_time (Date Time) - Today's date in UTC time
account-data-readme = ============================================
                      Thunderbird Appointment Data Download Readme
                      ============================================

                      Time of download (UTC): { $download_time }

                      Included in this zip is all of your user data from our system in .csv format.

                      ============================================
                      How Do I View it?
                      ============================================

                      You can open these .csv files in a variety applications like:
                       - Microsoft Excel
                       - Google Sheets
                       - Numbers
                       - LibreOffice Calc

                      ============================================
                      What's Included?
                      ============================================

                      Note: If a file is empty or blank then we don't have that type of data on record for you.

                      The following files are included:
                       - appointments.csv : A list of Appointments from our database
                       - attendees.csv : A list of Appointment Slot Attendees from our database
                       - calendars.csv : A list of Calendars from our database
                       - slots.csv : A list of Appointment Slots from our database.
                       - subscriber.csv : The personal information we store about you from our database.
                       - readme.txt : This file!

### Thunderbird Appointment Backend Strings

# Locale code
locale = en

## Health Check

# Should indicate application wellness.
health-ok = System is operational

## General Exceptions

account-delete-fail = There was a problem deleting your data. This incident has been logged and your data will manually be removed.

## Google Exceptions

google-connection-error = Error connecting with Google API, please re-connect.
google-scope-changed = You must enable Calendar and Event access to use Thunderbird Appointment.
google-invalid-creds = Google authentication credentials are not valid.
google-auth-fail = Google authentication failed.
google-auth-expired = Google authentication session expired, please try again.
google-sync-fail = An error occurred while syncing calendars. Please try again later.

## Frontend Facing Strings

# If the calendar event does not have a title this will be used instead
event-summary-not-found = Title not found!

## Event File Strings

# Variables:
# $url (String) - A link to the external meeting room for the meeting (e.g. Zoom meeting, Google Meets, Matrix chatroom, etc..)
join-online = Join online at: { $url }

# Variables:
# $phone (String) - An unformatted phone number for the meeting
join-phone = Join by phone: { $phone }

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

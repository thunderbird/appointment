### Thunderbird Appointment Backend Strings

# Locale code
locale = de

## Health Check

# Should indicate application wellness.
health-ok = Betriebsbereit

## General Exceptions

unknown-error = Ein unbekannter Fehler ist aufgetreten. Bitte später noch einmal versuchen.

appointment-not-found = Der Termin konnte nicht gefunden werden.
calendar-not-found = Der Kalender konnte nicht gefunden werden.
schedule-not-found = Der Zeitplan konnte nicht gefunden werden.
slot-not-found = Das gewählte Zeitfenster konnte nicht gefunden werden. Bitte erneut versuchen.
subscriber-not-found = Der Benutzer konnte nicht gefunden werden.

appointment-not-auth = Keine Berechtigung, diesen Termin einzusehen oder zu ändern.
calendar-not-auth = Keine Berechtigung, diesen Kalender anzusehen oder zu ändern.
schedule-not-auth = Keine Berechtigung, diesen Zeitplan einzusehen oder zu ändern.
slot-not-auth = Keine Berechtigung, dieses Zeitfenster zu sehen oder zu ändern.

account-delete-fail = Bei der Löschung der Daten ist ein Problem aufgetreten. Dieser Vorfall wurde protokolliert und die Daten werden manuell gelöscht.
protected-route-fail = Keine gültigen Authentifizierungsdaten angegeben.
username-not-available = Dieser Benutzername ist bereits vergeben.
invalid-link = Dieser Link ist nicht mehr gültig.
calendar-sync-fail = Bei der Synchronisierung von Kalendern ist ein Fehler aufgetreten. Bitte später noch einmal versuchen.
calendar-not-active = Der Kalender ist nicht verbunden.
slot-not-found = Es gibt keine freien Zeitfenster zu buchen.
slot-already-taken = Das gewählte Zeitfenster ist nicht mehr verfügbar. Bitte erneut versuchen.
slot-invalid-email = Die angegebene E-Mail-Adresse war nicht gültig. Bitte erneut versuchen.

schedule-not-active = Der Zeitplan wurde abgeschaltet. Bitte für weitere Informationen den Eigentümer des Zeitplans kontaktieren.

remote-calendar-connection-error = Der angebundene Kalender konnte nicht erreicht werden. Bitte die Verbindungsinformationen überprüfen und noch einmal versuchen.

event-could-not-be-accepted = Es ist ein Fehler bei der Annahme der Buchungsdaten aufgetreten. Bitte später noch einmal versuchen.

## Authentication Exceptions

email-mismatch = E-Mail-Adresse stimmen nicht überein.
invalid-credentials = Die angegebenen Anmeldedaten sind nicht gültig.
oauth-error = Es ist ein Fehler bei der Authentifizierung aufgetreten. Bitte erneut versuchen.

## Zoom Exceptions

zoom-not-connected = Es wird ein verbundenes Zoom-Konto benötigt, um einen Meeting-Link zu erstellen.

## Google Exceptions

google-connection-error = Fehler bei der Verbindung mit Google API, bitte Verbindung erneut herstellen.
google-scope-changed = Der Zugriff auf Kalender und Ereignisse muss aktiviert sein, um Thunderbird Appointment verwenden zu können.
google-invalid-creds = Die Anmeldedaten für die Google-Authentifizierung sind nicht gültig.
google-auth-fail = Google-Authentifizierung fehlgeschlagen.
google-auth-expired = Die Google-Authentifizierungssitzung ist abgelaufen, bitte erneut versuchen.
google-sync-fail = Bei der Synchronisierung von Kalendern ist ein Fehler aufgetreten. Bitte später noch einmal versuchen.
google-only-one = Es kann nur ein einziges Google-Konto verbunden sein.

## Frontend Facing Strings

# If the calendar event does not have a title this will be used instead
event-summary-not-found = Ereignis nicht gefunden!

## Event File Strings

# Variables:
# $url (String) - A link to the external meeting room for the meeting (e.g. Zoom meeting, Google Meets, Matrix chatroom, etc..)
join-online = Online teilnehmen unter: { $url }

# Variables:
# $phone (String) - An unformatted phone number for the meeting
join-phone = Per Telefon teilnehmen: { $phone }

## Account Data Readme

# This is a text file that is generated and bundled along with your account data
# Variables:
# $download_time (Date Time) - Today's date in UTC time
account-data-readme = ===============================================
                      Thunderbird Appointment Daten Download Liesmich
                      ===============================================

                      Download-Zeitpunkt (UTC): { $download_time }

                      In dieser Zip-Datei sind alle Benutzerdaten aus unserem System im CSV-Format enthalten.

                      ===============================================
                      Wie können die Daten eingesehen werden?
                      ===============================================

                      CSV-Dateien können in vielen Anwendungen geöffnet werden:
                       - Microsoft Excel
                       - Google Sheets
                       - Numbers
                       - LibreOffice Calc

                      ===============================================
                      Was ist enthalten?
                      ===============================================

                      Hinweis: Wenn eine Datei leer ist, ist diese Art von Daten nicht vorhanden.

                      Die folgenden Dateien sind enthalten:
                       - appointments.csv : Eine Liste von Terminen aus unserer Datenbank
                       - attendees.csv : Eine Liste von Termin-Teilnehmern aus unserer Datenbank
                       - calendars.csv : Eine Liste von Kalendern aus unserer Datenbank
                       - slots.csv : Eine Liste von Zeitfenstern aus unserer Datenbank.
                       - subscriber.csv : Die persönlichen Informationen, die wir von Benutzern in unserer Datenbank speichern.
                       - readme.txt : Diese Datei

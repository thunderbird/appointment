### Thunderbird Appointment Backend Email Strings

## General

-brand-name = Thunderbird Appointment
-brand-footer = Diese Nachricht wurde gesendet von {-brand-name}.

mail-brand-footer = {-brand-footer}

## Invitation

invite-mail-subject = Einladung gesendet von {-brand-name}
invite-mail-plain = {-brand-footer}

## New Booking

# Variables
# $name (String) - Name of the person who requested the appointment
new-booking-subject = Du hast eine neue bestätigte Terminbuchung mit { $name }
# Variables:
# $name (String) - Name of the person who requested the appointment
# $email (String) - Email of the person who requested the appointment
# $date (String) - Date of the Appointment
new-booking-plain = { $name } ({ $email }) hat soeben { $date } gebucht

                    {-brand-footer}

# Variables:
# $name (String) - Name of the person who requested the appointment
# $email (String) - Email of the person who requested the appointment
# $date (String) - Date of the requested appointment
# $schedule_name (String) - The name of the schedule used to book the appointment
# $duration (String) - Length of minutes the appointment will be
new-booking-html-heading-name = { $name }
new-booking-html-heading-email = ({ $email })
# FIXME: Google Translate Patch !
new-booking-html-heading-text = hat gerade Zeit im { $schedule_name } gebucht
new-booking-html-time = { $duration } mins

## Confirm Appointment

confirm-mail-subject = Buchungsanfrage von {-brand-name} bestätigen
# Variables:
# $name (String) - Name of the person who requested the appointment
# $email (String) - Email of the person who requested the appointment
# $duration (String) - Length of meeting in minutes
# $day (String) - Formatted date string
# $time_range (String) - Formatted time string
# $timezone (String) - Timezone (e.g. UTC, PST, etc...)
# $schedule_name - Name of the schedule the appointment was booked on
# $confirm_url (String) - URL that when clicked will confirm the appointment
# $deny_url (String) - URL that when clicked will deny the appointment
confirm-mail-plain = { $name } ({ $email }) hat soeben dieses Zeitfenster aus deinem Kalender angefordert:

                    { $duration } mins
                    { $time_range } ({ $timezone })
                    { $day }

                    Dieser Link führt zur Bestätigung der Buchungsanfrage:
                    { $confirm_url }

                    Dieser Link führt zur Ablehnung der Buchungsanfrage:
                    { $deny_url }

                    {-brand-footer}
# Variables:
# $name (String) - Name of the person who requested the appointment
# $email (String) - Email of the person who requested the appointment
# $date (String) - Date of the requested appointment
# $schedule_name (String) - The name of the schedule used to book the appointment
# $duration (String) - Length of minutes the appointment will be
# FIXME: Google Translation patch !
confirm-mail-html-heading-name = { $name }
confirm-mail-html-heading-email = ({ $email })
confirm-mail-html-heading-text = fordert die Buchung eines Zeitfensters in { $schedule_name } an
confirm-mail-html-time = { $duration } mins

confirm-mail-html-confirm-text = Dieser Link führt zur Bestätigung der Buchungsanfrage:
confirm-mail-html-confirm-action = Buchung bestätigen
confirm-mail-html-deny-text = Dieser Link führt zur Ablehnung der Buchungsanfrage:
confirm-mail-html-deny-action = Buchung ablehnen

## Rejected Appointment

reject-mail-subject = Buchungsanfrage abgelehnt
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
reject-mail-html-heading = { $owner_name } hat deine Buchungsanfrage für dieses Zeitfenster abgelehnt: { $date }.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
reject-mail-plain = { $owner_name } hat deine Buchungsanfrage für dieses Zeitfenster abgelehnt: { $date }.
                    {-brand-footer}

## Pending Appointment

pending-mail-subject = deine Buchungsanfrage wartet auf Bestätigung
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
pending-mail-html-heading = { $owner_name } wurde über deine Buchungsanfrage für dieses Zeitfenster informiert: { $date }. Du erhältst eine weitere E-Mail, sobald die Anfrage genehmigt oder abgelehnt wurde.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
pending-mail-plain = { $owner_name } wurde über deine Buchungsanfrage für dieses Zeitfenster informiert: { $date }.
                    Du erhältst eine weitere E-Mail, sobald die Anfrage genehmigt oder abgelehnt wurde.
                    {-brand-footer}

## Zoom Invite Link Failed

zoom-invite-failed-subject = Fehler Erstellung Zoom-Meeting
# Variables:
# $title - The appointment's title
zoom-invite-failed-html-heading = Leider ist bei der Erstellung des Zoom-Meetings für deinen nächsten Termin ein Fehler aufgetreten: { $title }.
# Variables:
# $title - The appointment's title
zoom-invite-failed-plain = Leider ist bei der Erstellung des Zoom-Meetings für deinen nächsten Termin ein Fehler aufgetreten: { $title }.
                           {-brand-footer}

## Support Request

# Variables:
# $topic (String) - Custom subject from the requestee
support-mail-subject = Supportanfrage: { $topic }
# Variables:
# $requestee_name (String) - Name of the person who did the request
# $requestee_email (String) - Email address of the person who did the request
support-mail-html-heading = { $requestee_name } ({ $requestee_email }) hat folgende Supportanfrage per Kontaktformular auf {-brand-name} gestellt.
# Variables:
# $topic (String) - Topic selected by the person who did the request
support-mail-html-topic = { $topic }
# Variables:
# $details (String) - Detailed description given by the person who did the request
support-mail-html-details = { $details }
# Variables:
# $requestee_name (String) - Name of the person who did the request
# $requestee_email (String) - Email address of the person who did the request
# $topic (String) - Topic selected by the person who did the request
# $details (String) - Detailed description given by the person who did the request
support-mail-plain = { $requestee_name } ({ $requestee_email }) hat folgende Supportanfrage per Kontaktformular auf {-brand-name} gestellt.
                    Thema: { $topic }
                    Inhalt: { $details }
                    {-brand-footer}

## New/Invited Account Email
new-account-mail-subject = Du wurdest zu Thunderbird Appointment eingeladen
new-account-mail-action = Weiter zu Thunderbird Appointment
new-account-mail-html-heading = Du wurdest zu Thunderbird Appointment eingeladen.
new-account-mail-html-body = Logge dich mit dieser E-Mail-Adresse ein um fortzufahren.
# Variables:
# $homepage_url (String) - URL to Thunderbird Appointment
new-account-mail-plain = Du wurdest zu Thunderbird Appointment eingeladen.
                    Logge dich mit dieser E-Mail-Adresse ein um fortzufahren.
                    { $homepage_url }
                    {-brand-footer}

## Confirm Email for waiting list
confirm-email-mail-subject = Bestätige deine E-Mail-Adresse um der Warteliste beizutreten!
confirm-email-mail-confirm-action = Bestätige deine E-Mail-Adresse
confirm-email-mail-decline-action = Entferne deine E-Mail-Adresse
confirm-email-mail-html-heading = Danke für Dein Interesse an Thunderbird Appointment.
confirm-email-mail-html-body = Bevor wir Dich auf unsere Warteliste setzen, musst Du Deine E-Mail-Adresse unten bestätigen.
confirm-email-mail-html-body-2 = Hast Du diese E-Mail irrtümlich erhalten, oder bist nicht mehr interessiert?
# Variables:
# $confirm_email_url (String) - URL to confirm your email
# $decline_email_url (String) - URL to remove the email from the waiting list
confirm-email-mail-plain = Danke für Dein Interesse an Thunderbird Appointment.
                    Bevor wir Dich auf unsere Warteliste setzen, musst Du Deine E-Mail-Adresse über den unten stehenden Link bestätigen.
                    { $confirm_email_url }

                    Hast Du diese E-Mail irrtümlich erhalten, oder bist nicht mehr interessiert? Folge einfach diesem Link, um Deine E-Mail-Adresse von der Warteliste zu löschen.
                    { $decline_email_url }
                    {-brand-footer}

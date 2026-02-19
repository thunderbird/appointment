### Thunderbird Appointment Backend Email Strings

## General

-brand-name = Thunderbird Appointment
-brand-slogan = Weniger planen, mehr schaffen.
-brand-sign-up-with-url = Registrieren auf appointment.day
-brand-sign-up-with-no-url = Registrieren auf
-brand-footer = Du erhälst diese E-Mail, weil Du dich auf unserer Website für Thunderbird Appointment Beta angemeldet hast.

                Copyright © 2025 MZLA Technologies. All rights reserved.
                MZLA Technologies 149 New Montgomery St., 4th Floor San Francisco, CA 94501 USA

mail-brand-contact-form = Kontaktformular
mail-brand-support-hint = Du hast Fragen? Wir helfen gern! Antworte einfach auf diese E-Mail für Support.
mail-brand-reply-hint = Du hast Fragen? Wir helfen gern! Du erreichst uns über unser { $contact_form_link }.
mail-brand-reply-hint-attendee-info = Du möchtest { $name } kontaktieren? Antworte einfach auf diese E-Mail.

mail-brand-footer = Du erhälst diese E-Mail, weil Du dich auf unserer Website für Thunderbird Appointment Beta angemeldet hast.

                    Copyright © 2025 MZLA Technologies. All rights reserved.
                    MZLA Technologies 149 New Montgomery St., 4th Floor San Francisco, CA 94501 USA
mail-brand-footer-privacy = Datenschutz
mail-brand-footer-legal = Impressum

## Invitation

invite-mail-subject = Buchung bestätigt von {-brand-name}
invite-mail-plain = {-brand-footer}

invite-mail-html-heading-name = { $name }
invite-mail-html-heading-email = ({ $email })
invite-mail-html-heading-text = hat deine Buchung bestätigt:
invite-mail-html-time = { $duration } min
invite-mail-html-invite-is-attached = Deine Kalendereinladung ist angehängt.
invite-mail-html-download = Download

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
new-booking-html-heading-text = hat gerade Zeit im { $schedule_name } gebucht
new-booking-html-time = { $duration } mins

## Confirm Appointment

# Variables
# $name (String) - Name of the person who requested the appointment
confirm-mail-subject = Buchungsanfrage von { $name } bestätigen
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
confirm-mail-html-heading-name = { $name }
confirm-mail-html-heading-email = ({ $email })
confirm-mail-html-heading-text = fordert die Buchung eines Zeitfensters in { $schedule_name } an
confirm-mail-html-time = { $duration } Minuten

confirm-mail-html-confirm-text = Dieser Link führt zur Bestätigung der Buchungsanfrage:
confirm-mail-html-confirm-action = Buchung bestätigen
confirm-mail-html-deny-text = Dieser Link führt zur Ablehnung der Buchungsanfrage:
confirm-mail-html-deny-action = Buchung ablehnen

## Cancelled Appointment

cancel-mail-subject = Buchungsanfrage abgesagt
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $day (String) - Localized date of the requested appointment
# $time_range (String) - Time range of the requested appointment (e.g. "14:00 - 14:30")
# $timezone (String) - Timezone abbreviation (e.g. "(CET)")
cancel-mail-html-heading = { $owner_name } hat deine Buchungsanfrage für { $day } um { $time_range } { $timezone } abgesagt.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $day (String) - Localized date of the requested appointment
# $time_range (String) - Time range of the requested appointment (e.g. "14:00 - 14:30")
# $timezone (String) - Timezone abbreviation (e.g. "(CET)")
cancel-mail-plain = { $owner_name } hat deine Buchungsanfrage für { $day } um { $time_range } { $timezone } abgesagt.
{-brand-footer}

## Rejected Appointment

reject-mail-subject = Buchungsanfrage abgelehnt
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $day (String) - Localized date of the requested appointment
# $time_range (String) - Time range of the requested appointment (e.g. "14:00 - 14:30")
# $timezone (String) - Timezone abbreviation (e.g. "(CET)")
reject-mail-html-heading = { $owner_name } hat deine Buchungsanfrage für { $day } um { $time_range } { $timezone } abgelehnt.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $day (String) - Localized date of the requested appointment
# $time_range (String) - Time range of the requested appointment (e.g. "14:00 - 14:30")
# $timezone (String) - Timezone abbreviation (e.g. "(CET)")
reject-mail-plain = { $owner_name } hat deine Buchungsanfrage für { $day } um { $time_range } { $timezone } abgelehnt.
                    {-brand-footer}

## Pending Appointment

pending-mail-subject = Deine Buchungsanfrage wartet auf Bestätigung
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $day (String) - Localized date of the requested appointment
# $time_range (String) - Time range of the requested appointment (e.g. "14:00 - 14:30")
# $timezone (String) - Timezone abbreviation (e.g. "(CET)")
pending-mail-html-heading = { $owner_name } wurde über deine Buchungsanfrage für { $day } um { $time_range } { $timezone } informiert. Du erhältst eine weitere E-Mail, sobald die Anfrage genehmigt oder abgelehnt wurde.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $day (String) - Localized date of the requested appointment
# $time_range (String) - Time range of the requested appointment (e.g. "14:00 - 14:30")
# $timezone (String) - Timezone abbreviation (e.g. "(CET)")
pending-mail-plain = { $owner_name } wurde über deine Buchungsanfrage für { $day } um { $time_range } { $timezone } informiert.
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

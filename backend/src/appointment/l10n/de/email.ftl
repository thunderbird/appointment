### Thunderbird Appointment Backend Email Strings

## General

-brand-name = Thunderbird Appointment
-brand-footer = Diese Nachricht wurde gesendet von {-brand-name}.

mail-brand-footer = {-brand-footer}

## Invitation

invite-mail-subject = Einladung gesendet von {-brand-name}
invite-mail-plain = {-brand-footer}
invite-mail-html = {-brand-footer}

## Confirm Appointment

confirm-mail-subject = Buchungsanfrage von {-brand-name} bestätigen
# Variables:
# $attendee_name (String) - Name of the person who requested the appointment
# $appointment_email (String) - Email of the person who requested the appointment
# $date (String) - Date of the Appointment
# $confirm_url (String) - URL that when clicked will confirm the appointment
# $deny_url (String) - URL that when clicked will deny the appointment
confirm-mail-plain = { $attendee_name } ({ $attendee_email }) hat soeben dieses Zeitfenster aus Deinem Kalender angefordert: { $date }

                    Dieser Link führt zur Bestätigung der Buchungsanfrage:
                    { $confirm_url }

                    Dieser Link führt zur Ablehnung der Buchungsanfrage:
                    { $deny_url }

                    {-brand-footer}
# Variables:
# $attendee_name (String) - Name of the person who requested the appointment
# $appointment_email (String) - Email of the person who requested the appointment
# $date (String) - Date of the requested appointment
confirm-mail-html-heading = { $attendee_name } ({ $attendee_email })  hat soeben dieses Zeitfenster aus Deinem Kalender angefordert: { $date }.
confirm-mail-html-confirm-text = Dieser Link führt zur Bestätigung der Buchungsanfrage:
confirm-mail-html-confirm-action = Buchung bestätigen
confirm-mail-html-deny-text = Dieser Link führt zur Ablehnung der Buchungsanfrage:
confirm-mail-html-deny-action = Buchung ablehnen

## Rejected Appointment

reject-mail-subject = Buchungsanfrage abgelehnt
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
reject-mail-html-heading = { $owner_name } hat Deine Buchungsanfrage für dieses Zeitfenster abgelehnt: { $date }.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
reject-mail-plain = { $owner_name } hat Deine Buchungsanfrage für dieses Zeitfenster abgelehnt: { $date }.
                    {-brand-footer}

## Pending Appointment
pending-mail-subject = Deine Buchungsanfrage wartet auf Bestätigung
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
pending-mail-html-heading = { $owner_name } wurde über Deine Buchungsanfrage für dieses Zeitfenster informiert: { $date }. Du erhälst eine weitere E-Mail, sobald die Anfrage genehmigt oder abgelehnt wurde.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
pending-mail-plain = { $owner_name } wurde über Deine Buchungsanfrage für dieses Zeitfenster informiert: { $date }.
                    Du erhälst eine weitere E-Mail, sobald die Anfrage genehmigt oder abgelehnt wurde.
                    {-brand-footer}

## Zoom Invite Link Failed

zoom-invite-failed-subject = Fehler Erstellung Zoom-Meeting
# Variables:
# $title - The appointment's title
zoom-invite-failed-html-heading = Leider ist bei der Erstellung des Zoom-Meetings für Deinen nächsten Termin ein Fehler aufgetreten: { $title }.
# Variables:
# $title - The appointment's title
zoom-invite-failed-plain = Leider ist bei der Erstellung des Zoom-Meetings für Deinen nächsten Termin ein Fehler aufgetreten: { $title }.
                           {-brand-footer}

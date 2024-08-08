### Thunderbird Appointment Backend Email Strings

## General

-brand-name = Thunderbird Appointment
-brand-slogan = Plan less, do more.
-brand-sign-up-with-url = Sign up on appointment.day
-brand-sign-up-with-no-url = Sign up on
-brand-footer = This message was sent from:
                {-brand-name}
                {-brand-slogan} {-brand-sign-up-with-url}

mail-brand-footer = This message was sent from:
                    {-brand-name}
                    {-brand-slogan} {-brand-sign-up-with-no-url}

## Invitation

invite-mail-subject = Invitation sent from {-brand-name}
invite-mail-plain = {-brand-footer}
invite-mail-html = {-brand-footer}

invite-mail-html-heading-name = { $name }
invite-mail-html-heading-email = ({ $email })
invite-mail-html-heading-text = has accepted your booking:
invite-mail-html-time = { $duration } mins
invite-mail-html-invite-is-attached = You can download the calendar invite file below:
invite-mail-html-download = Download

## New Booking

# Variables
# $attendee_name (String) - Name of the person who requested the appointment
new-booking-subject = You have a new confirmed booking with { $attendee_name }
# Variables:
# $attendee_name (String) - Name of the person who requested the appointment
# $appointment_email (String) - Email of the person who requested the appointment
# $date (String) - Date of the Appointment
new-booking-plain = { $attendee_name } ({ $attendee_email }) has just booked { $date }

                    {-brand-footer}

# Variables:
# $attendee_name (String) - Name of the person who requested the appointment
# $appointment_email (String) - Email of the person who requested the appointment
# $date (String) - Date of the requested appointment
new-booking-html-heading = { $attendee_name } ({ $attendee_email }) has just booked { $date }

## Confirm Appointment

# Variables
# $attendee_name (String) - Name of the person who requested the appointment
confirm-mail-subject = Action Required: Confirm booking request from { $attendee_name }
# Variables:
# $attendee_name (String) - Name of the person who requested the appointment
# $appointment_email (String) - Email of the person who requested the appointment
# $date (String) - Date of the Appointment
# $confirm_url (String) - URL that when clicked will confirm the appointment
# $deny_url (String) - URL that when clicked will deny the appointment
confirm-mail-plain = { $name } ({ $email }) is requesting to book a time slot in: { $schedule_name }

                    { $duration } mins
                    { $time_range } ({ $timezone })
                    { $day }

                    Visit this link to confirm the booking request:
                    { $confirm_url }

                    Or this link if you want to deny it:
                    { $deny_url }

                    {-brand-footer}
# Variables:
# $attendee_name (String) - Name of the person who requested the appointment
# $appointment_email (String) - Email of the person who requested the appointment
# $date (String) - Date of the requested appointment
confirm-mail-html-heading-name = { $name }
confirm-mail-html-heading-email = ({ $email })
confirm-mail-html-heading-text = is requesting to book a time slot in { $schedule_name }:
confirm-mail-html-time = { $duration } mins

confirm-mail-html-confirm-text = Click here to confirm the booking request:
confirm-mail-html-confirm-action = Confirm
confirm-mail-html-deny-text = Or here if you want to deny it:
confirm-mail-html-deny-action = Decline

## Rejected Appointment

reject-mail-subject = Booking request declined
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
reject-mail-html-heading = { $owner_name } denied your booking request for this time slot: { $date }.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
reject-mail-plain = { $owner_name } denied your booking request for this time slot: { $date }.
                    {-brand-footer}

## Pending Appointment

pending-mail-subject = Your booking request is pending approval
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
pending-mail-html-heading = { $owner_name } has been notified of your booking request for this time slot: { $date }. You will receive another email once that request has been approved or declined.
# Variables:
# $owner_name (String) - Name of the person who owns the schedule
# $date (String) - Date of the requested appointment
pending-mail-plain = { $owner_name } has been notified of your booking request for this time slot: { $date }.
                    You will receive another email once that request has been approved or declined.
                    {-brand-footer}

## Zoom Invite Link Failed

zoom-invite-failed-subject = Zoom Meeting Link Creation Error
# Variables:
# $title - The appointment's title
zoom-invite-failed-html-heading = Unfortunately there was an error creating your Zoom meeting for your upcoming appointment: { $title }.
# Variables:
# $title - The appointment's title
zoom-invite-failed-plain = Unfortunately there was an error creating your Zoom meeting for your upcoming appointment: { $title }.
                           {-brand-footer}

## Support Request

# Variables:
# $topic (String) - Custom subject from the requestee
support-mail-subject = Support request: { $topic }
# Variables:
# $requestee_name (String) - Name of the person who did the request
# $requestee_email (String) - Email address of the person who did the request
support-mail-html-heading = { $requestee_name } ({ $requestee_email }) send the following request via the support form on {-brand-name}.
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
support-mail-plain = { $requestee_name } ({ $requestee_email }) sent the following request via the support form on {-brand-name}.
                    Topic: { $topic }
                    Details: { $details }
                    {-brand-footer}

## New/Invited Account Email
new-account-mail-subject = You've been invited to Thunderbird Appointment
new-account-mail-action = Continue to Thunderbird Appointment
new-account-mail-html-heading = You've been invited to Thunderbird Appointment. Login with this email address to continue.
# Variables:
# $homepage_url (String) - URL to Thunderbird Appointment
new-account-mail-plain = You've been invited to Thunderbird Appointment.
                    Login with this email address to continue.
                    { $homepage_url }
                    {-brand-footer}

## Confirm Email for waiting list
confirm-email-mail-subject = Confirm your email to join the waiting list!
confirm-email-mail-confirm-action = Confirm your email
confirm-email-mail-decline-action = Remove your email
confirm-email-mail-html-body = Thank you for your interest in Thunderbird Appointment.
                               Before we add you to our waiting list we need you to confirm your email address below.
confirm-email-mail-html-body-2 = Did you receive this email in error, or are you no longer interested?
# Variables:
# $confirm_email_url (String) - URL to confirm your email
# $decline_email_url (String) - URL to remove the email from the waiting list
confirm-email-mail-plain = Thank you for your interest in Thunderbird Appointment.
                    Before we add you to our waiting list we need you to confirm your email address at the link below.
                    { $confirm_email_url }

                    Did you receive this email in error, or are you no longer interested? Just follow this link to remove your email from our waiting list.
                    { $decline_email_url }
                    {-brand-footer}

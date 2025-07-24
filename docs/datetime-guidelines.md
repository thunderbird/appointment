# Datetime Guidelines

This is a short document intending to inform the reader of how we handle (or should be handling) datetimes in
Appointment.

## Facts

### All server datetime and time fields should be stored as UTC time

This normalizes datetime / time fields so we don't have to worry about not including timezone information,
or doing any timezone comparisons when simply looking up a time or datetime.

### All schedule comparisons should be converted and compared in the schedule owner's timezone

This eliminates any day overflow errors when comparing a start and end time.

For example, if someone wants to set their availability to `9 to 17` (`9am to 5pm`) America/Vancouver
(Daylight savings - GMT-7) the server should not do this check in UTC as that would convert to `16 to 0` and the check
would fail.

### The server should be the one converting dates

To avoid having to re-convert datetime fields during comparisons the server / backend should be tasked with converting
datetime fields to UTC not the frontend.

### Day comparisons should be calculated via the `toordinal()` function of a datetime object

If you're comparing two dates against each other, do not use the current day of the month. Use the datetime fields
`toordinal()` function. This value is the absolute integer and incremented from by day starting from Jan 1st Year 1.

This avoids having to take into account the month and year when the dates are cross-month or cross-year.

### Test!

Make sure to well test your scheduling code. You can use freezegun's freeze_time helper to test against specific
datetime scenarios with ease.


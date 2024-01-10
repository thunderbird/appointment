from fastapi import HTTPException

from ..l10n import l10n


class APIException(HTTPException):
    """Base exception for all custom API exceptions
    Custom messages are defined in a function, because l10n needs context set before use."""
    status_code = 500

    def __init__(self, **kwargs):
        super().__init__(status_code=self.status_code, detail=self.get_msg(), **kwargs)

    def get_msg(self):
        return l10n('unknown-error')


class InvalidTokenException(APIException):
    """Raise when the subscriber could not be parsed from the auth token"""
    status_code = 401

    def get_msg(self):
        return l10n('protected-route-fail')


class InvalidLinkException(APIException):
    """Raise when verify_subscriber_link fails"""
    status_code = 400

    def get_msg(self):
        return l10n('invalid-link')


class SubscriberNotFoundException(APIException):
    """Raise when the calendar is not found during route validation"""
    status_code = 404

    def get_msg(self):
        return l10n('subscriber-not-found')


class CalendarNotFoundException(APIException):
    """Raise when the calendar is not found during route validation"""
    status_code = 404

    def get_msg(self):
        return l10n('calendar-not-found')


class CalendarNotAuthorizedException(APIException):
    """Raise when the calendar is owned by someone else during route validation"""
    status_code = 403

    def get_msg(self):
        return l10n('calendar-not-auth')


class CalendarNotConnectedException(APIException):
    """Raise when the calendar is owned by someone else during route validation"""
    status_code = 403

    def get_msg(self):
        return l10n('calendar-not-active')


class AppointmentNotFoundException(APIException):
    """Raise when the appointment is not found during route validation"""
    status_code = 404

    def get_msg(self):
        return l10n('appointment-not-found')


class AppointmentNotAuthorizedException(APIException):
    """Raise when the appointment is owned by someone else during route validation"""
    status_code = 403

    def get_msg(self):
        return l10n('appointment-not-auth')


class ScheduleNotFoundException(APIException):
    """Raise when the schedule is not found during route validation"""
    status_code = 404

    def get_msg(self):
        return l10n('schedule-not-found')
    

class ScheduleNotAuthorizedException(APIException):
    """Raise when the schedule is owned by someone else during route validation"""
    status_code = 403

    def get_msg(self):
        return l10n('schedule-not-auth')


class SlotNotFoundException(APIException):
    """Raise when a timeslot is not found during route validation"""
    status_code = 404

    def get_msg(self):
        return l10n('slot-not-found')


class SlotAlreadyTakenException(APIException):
    """Raise when a timeslot is already taken during route validation"""
    status_code = 403

    def get_msg(self):
        return l10n('slot-already-taken')


class SlotNotAuthorizedException(APIException):
    """Raise when a slot is owned by someone else during route validation"""
    status_code = 403
    
    def get_msg(self):
        return l10n('slot-not-auth')


class ZoomNotConnectedException(APIException):
    """Raise if the user requires a zoom connection during route validation"""
    status_code = 400

    def get_msg(self):
        return l10n('zoom-not-connected')

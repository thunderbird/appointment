from fastapi import HTTPException

from ..l10n import l10n


class APIInvalidToken(HTTPException):
    """Raise when the subscriber could not be parsed from the auth token"""
    def __init__(self, **kwargs):
        super().__init__(status_code=401, detail=l10n('protected-route-fail'), **kwargs)


class APISubscriberNotFound(HTTPException):
    """Raise when the calendar is not found during route validation"""
    def __init__(self, **kwargs):
        super().__init__(status_code=404, detail=l10n('calendar-not-found'), **kwargs)


class APICalendarNotFound(HTTPException):
    """Raise when the calendar is not found during route validation"""
    def __init__(self, **kwargs):
        super().__init__(status_code=404, detail=l10n('calendar-not-found'), **kwargs)


class APICalendarNotAuthorized(HTTPException):
    """Raise when the calendar is owned by someone else during route validation"""
    def __init__(self, **kwargs):
        super().__init__(status_code=403, detail=l10n('calendar-not-auth'), **kwargs)


class APIAppointmentNotFound(HTTPException):
    """Raise when the appointment is not found during route validation"""
    def __init__(self, **kwargs):
        super().__init__(status_code=404, detail=l10n('appointment-not-found'), **kwargs)


class APIAppointmentNotAuthorized(HTTPException):
    """Raise when the appointment is owned by someone else during route validation"""
    def __init__(self, **kwargs):
        super().__init__(status_code=403, detail=l10n('appointment-not-auth'), **kwargs)

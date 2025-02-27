from fastapi import HTTPException

from ..l10n import l10n


class APIException(HTTPException):
    """Base exception for all custom API exceptions
    Custom messages are defined in a function, because l10n needs context set before use."""

    id_code = 'UNKNOWN'
    status_code = 500
    message_key = None
    reason = None

    def __init__(self, reason: str|None = None, **kwargs):
        message_key = kwargs.pop('message_key', False)
        if message_key is not False:
            self.message_key = message_key

        if reason:
            self.reason = reason

        super().__init__(
            status_code=self.status_code,
            detail={
                'id': self.id_code,
                'reason': self.get_reason(),
                'message': self.get_msg(),
                'status': self.status_code,
            },
            **kwargs,
        )

    def get_msg(self):
        if self.message_key:
            return l10n(self.message_key)

        return l10n('unknown-error')

    def get_reason(self):
        return self.reason

class InvalidPermissionLevelException(APIException):
    """Raise when the subscribers permission level is too low for the action"""

    id_code = 'INVALID_PERMISSION_LEVEL'
    status_code = 401

    def get_msg(self):
        return l10n('protected-route-fail')


class InvalidTokenException(APIException):
    """Raise when the subscriber could not be parsed from the auth token"""

    id_code = 'INVALID_TOKEN'
    status_code = 401

    def get_msg(self):
        return l10n('protected-route-fail')


class InvalidLinkException(APIException):
    """Raise when subscriber.verify_link fails"""

    id_code = 'INVALID_LINK'
    status_code = 400

    def get_msg(self):
        return l10n('invalid-link')


class SubscriberNotFoundException(APIException):
    """Raise when the subscriber is not found during route validation"""

    id_code = 'SUBSCRIBER_NOT_FOUND'
    status_code = 404

    def get_msg(self):
        return l10n('subscriber-not-found')


class CalendarNotFoundException(APIException):
    """Raise when the calendar is not found during route validation"""

    id_code = 'CALENDAR_NOT_FOUND'
    status_code = 404

    def get_msg(self):
        return l10n('calendar-not-found')


class CalendarNotAuthorizedException(APIException):
    """Raise when the calendar is owned by someone else during route validation"""

    id_code = 'CALENDAR_NOT_AUTH'
    status_code = 403

    def get_msg(self):
        return l10n('calendar-not-auth')


class CalendarNotConnectedException(APIException):
    """Raise when the calendar is owned by someone else during route validation"""

    id_code = 'CALENDAR_NOT_CONNECTED'
    status_code = 403

    def get_msg(self):
        return l10n('calendar-not-active')


class AppointmentNotFoundException(APIException):
    """Raise when the appointment is not found during route validation"""

    id_code = 'APPOINTMENT_NOT_FOUND'
    status_code = 404

    def get_msg(self):
        return l10n('appointment-not-found')


class AppointmentNotAuthorizedException(APIException):
    """Raise when the appointment is owned by someone else during route validation"""

    id_code = 'APPOINTMENT_NOT_AUTH'
    status_code = 403

    def get_msg(self):
        return l10n('appointment-not-auth')


class ScheduleNotFoundException(APIException):
    """Raise when the schedule is not found during route validation"""

    id_code = 'SCHEDULE_NOT_FOUND'
    status_code = 404

    def get_msg(self):
        return l10n('schedule-not-found')


class ScheduleNotActive(APIException):
    """Raise when the schedule is not active"""

    id_code = 'SCHEDULE_NOT_ACTIVE'
    status_code = 404

    def get_msg(self):
        return l10n('schedule-not-active')


class ScheduleNotAuthorizedException(APIException):
    """Raise when the schedule is owned by someone else during route validation"""

    id_code = 'SCHEDULE_NOT_AUTH'
    status_code = 403

    def get_msg(self):
        return l10n('schedule-not-auth')


class ScheduleCreationException(APIException):
    """Raise when we have an error with schedule creation but don't want to give exactly what."""
    id_code = 'SCHEDULE_CREATION_EXCEPTION'
    status_code = 500

    def get_msg(self):
        return l10n('unknown-error')


class SlotNotFoundException(APIException):
    """Raise when a timeslot is not found during route validation"""

    id_code = 'SLOT_NOT_FOUND'
    status_code = 404

    def get_msg(self):
        return l10n('slot-not-found')


class SlotAlreadyTakenException(APIException):
    """Raise when a timeslot is already taken during route validation"""

    id_code = 'SLOT_ALREADY_TAKEN'
    status_code = 403

    def get_msg(self):
        return l10n('slot-already-taken')


class SlotNotAuthorizedException(APIException):
    """Raise when a slot is owned by someone else during route validation"""

    id_code = 'SLOT_NOT_AUTH'
    status_code = 403

    def get_msg(self):
        return l10n('slot-not-auth')


class ZoomNotConnectedException(APIException):
    """Raise if the user requires a zoom connection during route validation"""

    id_code = 'ZOOM_NOT_CONNECTED'
    status_code = 400

    def get_msg(self):
        return l10n('zoom-not-connected')


class RemoteCalendarConnectionError(APIException):
    id_code = 'REMOTE_CALENDAR_CONNECTION_ERROR'
    status_code = 400

    def get_msg(self):
        return l10n('remote-calendar-connection-error')


class EventCouldNotBeAccepted(APIException):
    id_code = 'EVENT_COULD_NOT_BE_ACCEPTED'
    status_code = 400

    def get_msg(self):
        return l10n('event-could-not-be-accepted')


class EventCouldNotBeDeleted(APIException):
    id_code = 'EVENT_COULD_NOT_BE_DELETED'
    status_code = 400

    def get_msg(self):
        return l10n('event-could-not-be-deleted')


class InviteCodeNotFoundException(APIException):
    """Raise when the invite code is not found during route validation"""

    id_code = 'INVITE_CODE_NOT_FOUND'
    status_code = 404

    def get_msg(self):
        return l10n('invite-code-not-valid')


class InviteCodeNotAvailableException(APIException):
    """Raise when the invite code is not available anymore during route validation"""

    id_code = 'INVITE_CODE_NOT_AVAILABLE'
    status_code = 403

    def get_msg(self):
        return l10n('invite-code-not-valid')


class CreateSubscriberFailedException(APIException):
    """Raise when a subscriber failed to be created"""

    id_code = 'CREATE_SUBSCRIBER_FAILED'
    status_code = 400

    def get_msg(self):
        return l10n('failed-to-create-subscriber')


class CreateSubscriberAlreadyExistsException(APIException):
    """Raise when a subscriber failed to be created"""

    id_code = 'CREATE_SUBSCRIBER_ALREADY_EXISTS'
    status_code = 400

    def get_msg(self):
        return l10n('subscriber-already-exists')


class SubscriberAlreadyDeletedException(APIException):
    """Raise when a subscriber failed to be marked deleted because they already are"""

    id_code = 'SUBSCRIBER_ALREADY_DELETED'
    status_code = 400

    def get_msg(self):
        return l10n('subscriber-already-deleted')


class SubscriberAlreadyEnabledException(APIException):
    """Raise when a subscriber failed to be marked undeleted because they already are"""

    id_code = 'SUBSCRIBER_ALREADY_ENABLED'
    status_code = 400

    def get_msg(self):
        return l10n('subscriber-already-enabled')


class SubscriberSelfDeleteException(APIException):
    """Raise when a subscriber tries to delete themselves where not allowed"""

    id_code = 'SUBSCRIBER_SELF_DELETE'
    status_code = 403

    def get_msg(self):
        return l10n('subscriber-self-delete')


class WaitingListActionFailed(APIException):
    """Raise if the waiting list link was valid but failed for some reason"""

    id_code = 'WAITING_LIST_FAIL'
    status_code = 400

    def get_msg(self):
        return l10n('unknown-error')


class OAuthFlowNotFinished(APIException):
    """Raise when an oauth flow was started but not finished. Used for FTUE. Please override message_key."""

    id_code = 'OAUTH_FLOW_NOT_FINISHED'
    status_code = 400
    message_key = 'oauth-error'  # By default


class APIRateLimitExceeded(APIException):
    """Is raised when rate limit is exceeded"""

    id_code = 'RATE_LIMIT_EXCEEDED'
    status_code = 429

    def get_msg(self):
        return l10n('rate-limit-exceeded')


class GoogleCaldavNotSupported(APIException):
    """Is raised when an attempt to access the Google CalDAV API was detected"""

    id_code = 'GOOGLE_CALDAV_NOT_SUPPORTED'
    status_code = 400

    def get_msg(self):
        return l10n('google-caldav-not-supported')

    def get_reason(self):
        return l10n('google-caldav-not-supported-details')

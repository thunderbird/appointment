from .validation import APIException
from ..l10n import l10n


class GoogleScopeChanged(Exception):
    """Raise when Google API lets us know the scope has changed. Right now we require all requested scopes."""

    pass


class GoogleInvalidCredentials(Exception):
    """Raise when invalid credentials are passed and returned from Google API"""

    pass


class APIGoogleRefreshError(APIException):
    """Raise when you need to signal to the end-user that they need to re-connect to Google."""
    id_code = 'GOOGLE_REFRESH_ERROR'
    status_code = 401

    def get_msg(self):
        return l10n('google-connection-error')

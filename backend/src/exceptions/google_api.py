class GoogleScopeChanged(Exception):
    """Raise when Google API lets us know the scope has changed. Right now we require all requested scopes."""

    pass


class GoogleInvalidCredentials(Exception):
    """Raise when invalid credentials are passed and returned from Google API"""

    pass

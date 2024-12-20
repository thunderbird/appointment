class EventNotCreatedException(Exception):
    """Raise if an event cannot be created on a remote calendar"""

    pass


class EventNotDeletedException(Exception):
    """Raise if an event cannot be deleted on a remote calendar"""

    pass


class TestConnectionFailed(Exception):
    """Raise if test connection fails, include remote error message."""

    def __init__(self, reason: str | None = None):
        self.reason = reason

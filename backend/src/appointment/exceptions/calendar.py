class EventNotCreatedException(Exception):
    """Raise if an event cannot be created on a remote calendar"""

    pass


class FreeBusyTimeException(Exception):
    """Generic error with the free busy time api"""
    pass

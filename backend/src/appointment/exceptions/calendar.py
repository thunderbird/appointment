class EventNotCreatedException(Exception):
    """Raise if an event cannot be created on a remote calendar"""
    pass


class EventNotDeletedException(Exception):
    """Raise if an event cannot be deleted on a remote calendar"""
    pass

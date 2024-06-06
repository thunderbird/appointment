class NotInAllowListException(Exception):
    """Is raised when a given email is not in the allow list"""

    pass


class MissingRefreshTokenException(Exception):
    pass

import logging


class AccountDeletionException(Exception):
    def __init__(self, subscriber_id, message=""):
        super().__init__(message)
        self.subscriber_id = subscriber_id
        self.message = message

        # TODO: These fails are important to follow up on manually.
        # We'll need to raise this in our eventual error reporting service, or email.
        logging.error(f"Account deletion error for subscriber {subscriber_id}!")


class AccountDeletionPartialFail(AccountDeletionException):
    """Raise if the account deletion function doesn't delete all of the subscriber personal data"""

    pass


class AccountDeletionSubscriberFail(AccountDeletionException):
    """Raise if the account deletion function doesn't delete the subscriber"""

    pass

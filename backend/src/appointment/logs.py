import logging


class AccessLogLevelFilter(logging.Filter):
    """
    Because random sites can send junk, log 4XX at WARN level to Sentry noise
    5XX conditions are considered errors and will be sent to Sentry.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        status_code = record.args[-1] if record.args else None
        if isinstance(status_code, int) and 400 <= status_code < 500:
            record.levelno = logging.WARNING
            record.levelname = logging.getLevelName(logging.WARNING)
        elif isinstance(status_code, int) and status_code >= 500:
            record.levelno = logging.ERROR
            record.levelname = logging.getLevelName(logging.ERROR)
        return True

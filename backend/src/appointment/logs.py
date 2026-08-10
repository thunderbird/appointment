import logging


class AccessLogLevelFilter(logging.Filter):
    """Elevate uvicorn access log records for failed requests (status >= 400) to ERROR."""

    def filter(self, record: logging.LogRecord) -> bool:
        status_code = record.args[-1] if record.args else None
        if isinstance(status_code, int) and status_code >= 400:
            record.levelno = logging.ERROR
            record.levelname = logging.getLevelName(logging.ERROR)
        return True

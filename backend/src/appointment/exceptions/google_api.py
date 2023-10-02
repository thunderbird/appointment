from typing import Any, Optional, Dict

from fastapi import HTTPException


class GoogleScopeChanged(Exception):
    """Raise when Google API lets us know the scope has changed. Right now we require all requested scopes."""

    pass


class GoogleInvalidCredentials(Exception):
    """Raise when invalid credentials are passed and returned from Google API"""

    pass


class APIGoogleRefreshError(HTTPException):
    """Raise when you need to signal to the end-user that they need to re-connect to Google."""

    def __init__(
        self,
        message: str = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        detail = {
            "error": "google_refresh_error",
            "message": message if message is not None else "Error connecting with Google API, please re-connect.",
        }
        super().__init__(status_code=401, detail=detail, headers=headers)

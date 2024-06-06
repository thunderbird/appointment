from datetime import datetime, timedelta

DATEFMT = "%Y-%m-%d"

now = datetime.today()
DAY1 = now.strftime(DATEFMT)
DAY2 = (now + timedelta(days=1)).strftime(DATEFMT)
DAY3 = (now + timedelta(days=2)).strftime(DATEFMT)
DAY5 = (now + timedelta(days=4)).strftime(DATEFMT)
DAY14 = (now + timedelta(days=13)).strftime(DATEFMT)

# Standard headers to used for authentication requests
auth_headers = {"authorization": "Bearer testtokenplsignore"}

TEST_USER_ID = 1
TEST_CALDAV_URL = "https://caldav.example.org/"
TEST_CALDAV_USER = "Test"

# Default value for factories to use a random value
FAKER_RANDOM_VALUE = "___faker_random_value___"

FXA_CLIENT_PATCH = {
    "authorization_url": "https://www.example.org/login",
    "credentials_code": "1234",
    "external_connection_type_id": "abcd",
    "subscriber_email": "test2@example.org",
    "subscriber_avatar_url": "https://www.example.org/cool_pic.jpg",
    "subscriber_display_name": "test2",
}


def factory_has_value(val) -> bool:
    """For factories"""
    return val != FAKER_RANDOM_VALUE

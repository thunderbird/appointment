import json
import os


def normalize_secrets():
    """Normalizes AWS secrets for Appointment"""
    auth0_secrets = os.getenv("AUTH0_SECRETS")

    if auth0_secrets:
        secrets = json.loads(auth0_secrets)

        os.environ["AUTH0_API_DOMAIN"] = secrets.get("domain")
        os.environ["AUTH0_API_CLIENT_ID"] = secrets.get("client_id")
        os.environ["AUTH0_API_SECRET"] = secrets.get("secret")
        os.environ["AUTH0_API_AUDIENCE"] = secrets.get("audience")

    database_secrets = os.getenv("DATABASE_SECRETS")

    if database_secrets:
        secrets = json.loads(database_secrets)

        os.environ[
            "DATABASE_URL"
        ] = f"mysql+mysqldb://{secrets['username']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/appointment"

    database_enc_secret = os.getenv("DB_ENC_SECRET")

    if database_enc_secret:
        secrets = json.loads(database_enc_secret)

        os.environ["DB_SECRET"] = secrets.get("secret")
        # Technically not db related...might rename this item later.
        os.environ["SIGNED_SECRET"] = secrets.get("signed_secret")

    smtp_secrets = os.getenv("SMTP_SECRETS")

    if smtp_secrets:
        secrets = json.loads(smtp_secrets)

        os.environ["SMTP_SECURITY"] = "STARTTLS"
        os.environ["SMTP_URL"] = secrets.get("url")
        os.environ["SMTP_PORT"] = secrets.get("port")
        os.environ["SMTP_USER"] = secrets.get("username")
        os.environ["SMTP_PASS"] = secrets.get("password")
        os.environ["SMTP_SENDER"] = secrets.get("sender")

    google_oauth_secrets = os.getenv("GOOGLE_OAUTH_SECRETS")

    if google_oauth_secrets:
        secrets = json.loads(google_oauth_secrets)

        os.environ["GOOGLE_AUTH_CLIENT_ID"] = secrets.get("client_id")
        os.environ["GOOGLE_AUTH_SECRET"] = secrets.get("secret")
        os.environ["GOOGLE_AUTH_PROJECT_ID"] = secrets.get("project_id")
        os.environ["GOOGLE_AUTH_CALLBACK"] = secrets.get("callback_url")

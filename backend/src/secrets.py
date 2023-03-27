import json
import os


def normalize_secrets():
    """Normalizes AWS secrets for Appointment"""
    auth0_secrets = os.getenv('AUTH0_SECRETS')

    if auth0_secrets:
        secrets = json.loads(auth0_secrets)

        os.environ['AUTH0_API_DOMAIN'] = secrets.get('domain')
        os.environ['AUTH0_API_CLIENT_ID'] = secrets.get('client_id')
        os.environ['AUTH0_API_SECRET'] = secrets.get('secret')
        os.environ['AUTH0_API_AUDIENCE'] = secrets.get('audience')
        os.environ['AUTH0_SECRETS'] = ''

    database_secrets = os.getenv('DATABASE_SECRETS')

    if database_secrets:
        secrets = json.loads(database_secrets)

        os.environ['DATABASE_URL'] = f"mysql+mysqldb://{secrets['username']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/appointment"
        os.environ['DATABASE_SECRETS'] = ''

    database_enc_secret = os.getenv('DB_ENC_SECRET')

    if database_enc_secret:
        secrets = json.loads(database_enc_secret)

        os.environ['DB_SECRET'] = secrets.get('secret')
        os.environ['DB_ENC_SECRET'] = ''

    smtp_secrets = os.getenv('SMTP_SECRETS')

    if smtp_secrets:
        secrets = json.loads(smtp_secrets)

        os.environ['SMTP_SECURITY'] = 'STARTTLS'
        os.environ['SMTP_URL'] = secrets.get('url')
        os.environ['SMTP_PORT'] = secrets.get('port')
        os.environ['SMTP_USER'] = secrets.get('username')
        os.environ['SMTP_PASS'] = secrets.get('password')
        os.environ['SMTP_SECRETS'] = ''

import json
import os


def normalize_secrets():
    """Normalizes AWS secrets for Appointment"""
    database_secrets = os.getenv('DATABASE_SECRETS')

    if database_secrets:
        secrets = json.loads(database_secrets)

        host = secrets['host']
        port = secrets['port']

        # If port is not already in the host var, then append it to hostname
        hostname = host
        if f':{port}' not in host:
            hostname = f'{hostname}:{port}'

        os.environ['DATABASE_URL'] = (
            f"mysql+mysqldb://{secrets['username']}:{secrets['password']}@{hostname}/appointment"
        )

    database_enc_secret = os.getenv('DB_ENC_SECRET')

    if database_enc_secret:
        secrets = json.loads(database_enc_secret)

        os.environ['DB_SECRET'] = secrets.get('secret')
        # Technically not db related...might rename this item later.
        os.environ['SIGNED_SECRET'] = secrets.get('signed_secret')
        os.environ['SESSION_SECRET'] = secrets.get('session_secret')
        os.environ['JWT_SECRET'] = secrets.get('jwt_secret')

    smtp_secrets = os.getenv('SMTP_SECRETS')

    if smtp_secrets:
        secrets = json.loads(smtp_secrets)

        os.environ['SMTP_SECURITY'] = 'STARTTLS'
        os.environ['SMTP_URL'] = secrets.get('url')
        os.environ['SMTP_PORT'] = secrets.get('port')
        os.environ['SMTP_USER'] = secrets.get('username')
        os.environ['SMTP_PASS'] = secrets.get('password')
        os.environ['SUPPORT_EMAIL'] = secrets.get('support')

    google_oauth_secrets = os.getenv('GOOGLE_OAUTH_SECRETS')

    if google_oauth_secrets:
        secrets = json.loads(google_oauth_secrets)

        os.environ['GOOGLE_AUTH_CLIENT_ID'] = secrets.get('client_id')
        os.environ['GOOGLE_AUTH_SECRET'] = secrets.get('secret')
        os.environ['GOOGLE_AUTH_PROJECT_ID'] = secrets.get('project_id')
        os.environ['GOOGLE_AUTH_CALLBACK'] = secrets.get('callback_url')

    zoom_secrets = os.getenv('ZOOM_SECRETS')

    if zoom_secrets:
        secrets = json.loads(zoom_secrets)

        os.environ['ZOOM_AUTH_CLIENT_ID'] = secrets.get('client_id')
        os.environ['ZOOM_AUTH_SECRET'] = secrets.get('secret')

    fxa_secrets = os.getenv('FXA_SECRETS')

    if fxa_secrets:
        secrets = json.loads(fxa_secrets)

        os.environ['FXA_OPEN_ID_CONFIG'] = secrets.get('open_id_config')
        os.environ['FXA_CLIENT_ID'] = secrets.get('client_id')
        os.environ['FXA_SECRET'] = secrets.get('secret')
        os.environ['FXA_CALLBACK'] = secrets.get('callback_url')
        os.environ['FXA_ALLOW_LIST'] = secrets.get('allow_list')
        os.environ['APP_ADMIN_ALLOW_LIST'] = secrets.get('admin_list')

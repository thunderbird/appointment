import logging
import os
import requests
from ..database import models
from ..dependencies.database import get_engine_and_session


def export_users() -> None:
    """Export all users to Keycloak via API"""

    logging.info('Starting Keycloak user export via API...')

    # Get required environment variables
    tb_accounts_host = os.getenv('TB_ACCOUNTS_HOST')
    realm = os.getenv('KEYCLOAK_REALM')

    if not tb_accounts_host:
        logging.error('TB_ACCOUNTS_HOST environment variable is not set')
        raise ValueError('TB_ACCOUNTS_HOST environment variable is required')

    if not realm:
        logging.error('KEYCLOAK_REALM environment variable is not set')
        raise ValueError('KEYCLOAK_REALM environment variable is required')

    api_url = f'{tb_accounts_host}/admin/realms/{realm}/users'
    logging.info(f'Target API URL: {api_url}')

    _, session = get_engine_and_session()
    db = session()

    try:
        # Get all subscribers (not paginated for export)
        subscribers = db.query(models.Subscriber).all()
        total_users = len(subscribers)
        logging.info(f'Found {total_users} users to export')

        success_count = 0
        error_count = 0

        for idx, subscriber in enumerate(subscribers, 1):
            email = subscriber.email

            try:
                # Make POST request with only email field
                response = requests.post(
                    url=api_url,
                    json={
                        'email': email,
                        'emailVerified': 'true',
                        'username': subscriber.username
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=30,
                )

                response.raise_for_status()
                logging.info(f'[{idx}/{total_users}] Successfully exported user: {email}')
                success_count += 1

            except requests.HTTPError as e:
                logging.error(
                    f'[{idx}/{total_users}] Failed to export user {email}: '
                    f'HTTP {e.response.status_code} - {e.response.text}'
                )
                error_count += 1
            except requests.RequestException as e:
                logging.error(f'[{idx}/{total_users}] Request failed for user {email}: {str(e)}')
                error_count += 1

        logging.info(
            f'Export completed: {success_count} successful, {error_count} failed out of {total_users} total users'
        )

    finally:
        db.close()


def run():
    """Main entry point for the command"""
    export_users()

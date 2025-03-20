import os
import shutil

import dotenv
import secrets


def setup_accounts():
    if os.getenv('AUTH_SCHEME') != 'accounts':
        return

    print('Setting up accounts!')


def setup_env():
    """Goes through line-by-line and sets any empty values to the values in new_envs
    Also adds any keys that are in new_envs that are missing from .env"""
    print('Setting up env!')

    # Our new values!
    new_envs = {
        'DB_SECRET': secrets.token_hex(32),
        'SESSION_SECRET': secrets.token_hex(32),
        'JWT_SECRET': secrets.token_hex(32),
        'SIGNED_SECRET': secrets.token_hex(32),
        'APP_SETUP': 'True',
        'LOG_LEVEL': 'DEBUG',
        'APP_ENV': 'dev',
    }

    exists = os.path.isfile('.env')
    if not exists:
        print("Doesn't exist???")
        return None

    with open('.env', 'r') as fh:
        env_line = fh.readlines()

    with open('.env', 'w') as fh:
        for env in env_line:
            # Ignore empty lines, and comments
            if len(env.strip()) == 0 or env.lstrip().startswith('#'):
                fh.write(env)
                continue

            # None values
            if '=' not in env:
                # Special case for app setup!
                if env.strip() == 'APP_SETUP':
                    env = new_envs.get('APP_SETUP')
                    del new_envs['APP_SETUP']

                fh.write(env)
                continue

            key, value = env.split('=')

            if key in new_envs.keys():
                if len(value.strip()) == 0:
                    env = f'{key}={new_envs.get(key)}\n'
                del new_envs[key]

            fh.write(env)

        # Write any missing items out
        for key, value in new_envs.items():
            fh.write(f'{key}={new_envs.get(key)}\n')

    return dotenv.find_dotenv('.env')


def run():
    print('Checking if we need to run first time setup...')
    env = dotenv.find_dotenv('.env')

    if not env:
        exists = os.path.isfile('.env.example')
        if not exists:
            print('Err: Could not setup env, no example env?')
            return

        shutil.copy('.env.example', '.env')
        env = setup_env()

    dotenv.load_dotenv(env)

    if os.getenv('APP_SETUP'):
        print('App has previously been setup, skipping.')
        return

    env = setup_env()
    setup_accounts()

    if not env:
        print('Err: Could not setup env, permission issue?')
        return

    print('Finished running first time setup!')

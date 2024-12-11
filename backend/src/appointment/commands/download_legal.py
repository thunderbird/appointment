import os

import markupsafe
import requests
import markdown


def open_or_get(path: str):
    if path.startswith('http'):
        return requests.get(path).text

    # Otherwise it's a path
    with open(path, 'r') as fh:
        return fh.read()


def run():
    """Helper function to update privacy and terms.
    Please check to ensure you're not getting a 404 before committing lol.
    """
    print('Downloading the latest legal documents...')

    extensions = ['markdown.extensions.attr_list']
    # Only english for now. There's no german TB privacy policy?
    locales = ['en']

    for locale in locales:
        privacy_policy = os.getenv('TBA_PRIVACY_POLICY_LOCATION').format(locale=locale)
        terms_of_use = os.getenv('TBA_TERMS_OF_USE_LOCATION').format(locale=locale)

        os.makedirs(f'{os.path.dirname(__file__)}/../tmp/legal/{locale}', exist_ok=True)

        if privacy_policy:
            print('Privacy policy url found.')
            contents = open_or_get(privacy_policy)
            html = markupsafe.Markup(markdown.markdown(contents, extensions=extensions))

            with open(f'{os.path.dirname(__file__)}/../tmp/legal/{locale}/privacy.html', 'w') as fh:
                fh.write(html)

        if terms_of_use:
            print('Terms of use url found.')
            contents = open_or_get(terms_of_use)
            html = markupsafe.Markup(markdown.markdown(contents, extensions=extensions))

            with open(f'{os.path.dirname(__file__)}/../tmp/legal/{locale}/terms.html', 'w') as fh:
                fh.write(html)

    print('Done! Copy them over to the frontend/src/assets/legal!')

import os

import markupsafe
import requests
import markdown


def run():
    """Helper function to update privacy and terms. Please check to ensure you're not getting a 404 before committing lol."""
    print("Downloading the latest legal documents...")

    extensions = ['markdown.extensions.attr_list']
    # Only english for now. There's no german TB privacy policy?
    locales = ['en']

    for locale in locales:
        privacy_policy = os.getenv('TBA_PRIVACY_POLICY_URL').format(locale=locale)
        terms_of_use = os.getenv('TBA_TERMS_OF_USE_URL').format(locale=locale)

        if privacy_policy:
            print("Privacy policy url found.")
            contents = requests.get(privacy_policy).text
            html = markupsafe.Markup(markdown.markdown(contents, extensions=extensions))

            with open(f'{os.path.dirname(__file__)}/../templates/legal/{locale}/privacy.jinja2', 'w') as fh:
                fh.write(html)

        if terms_of_use:
            print("Terms of use url found.")
            contents = requests.get(terms_of_use).text
            html = markupsafe.Markup(markdown.markdown(contents, extensions=extensions))

            with open(f'{os.path.dirname(__file__)}/../templates/legal/{locale}/terms.jinja2', 'w') as fh:
                fh.write(html)

    print("Done!")

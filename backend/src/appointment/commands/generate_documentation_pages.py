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
    """Helper function to generate documentation/help pages into plain html"""
    print('Fetching documentation...')

    # Attr_List: In-case remote markdown has attributes
    # TOC: For ids on headers
    extensions = ['markdown.extensions.attr_list', 'markdown.extensions.toc']
    # Only english for now. There's no german TB privacy policy?
    locales = ['en']

    for locale in locales:
        using_zoom_doc = f'../docs/zoom/{locale}/using-zoom.md'

        os.makedirs(f'{os.path.dirname(__file__)}/../tmp/docs/{locale}', exist_ok=True)

        if using_zoom_doc:
            print('Using zoom doc found.')
            contents = open_or_get(using_zoom_doc)
            html = markupsafe.Markup(markdown.markdown(contents, extensions=extensions))

            with open(f'{os.path.dirname(__file__)}/../tmp/docs/{locale}/using-zoom.html', 'w') as fh:
                fh.write(html)

    print('Done! Copy them over to the frontend/src/assets/docs!')

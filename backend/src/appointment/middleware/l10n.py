import os

from starlette_context.plugins import Plugin
from fastapi import Request
from fluent.runtime import FluentLocalization, FluentResourceLoader

from ..defines import SUPPORTED_LOCALES, FALLBACK_LOCALE


class L10n(Plugin):
    """Provides fluent's format_value function via context['l10n']"""

    key = "l10n"

    def parse_accept_language(self, accept_language_header):
        languages = accept_language_header.split(",")
        parsed_locales = []

        for language in languages:
            split_language = language.split(";")
            if len(split_language) == 1:
                language = language.strip()
            else:
                language, _ = split_language
                language = language.strip()

            if language in SUPPORTED_LOCALES or language == "*":
                parsed_locales.append(language)

        if len(parsed_locales) == 0 or parsed_locales[0] == "*":
            parsed_locales = [FALLBACK_LOCALE]

        return parsed_locales

    def get_fluent(self, accept_languages):
        supported_locales = self.parse_accept_language(accept_languages)

        # Make sure our fallback locale is always in supported_locales
        if FALLBACK_LOCALE not in supported_locales:
            supported_locales.append(FALLBACK_LOCALE)

        base_url = "src/appointment/l10n"

        loader = FluentResourceLoader(f"{base_url}/{{locale}}")
        fluent = FluentLocalization(supported_locales, ["main.ftl", "email.ftl"], loader)

        return fluent.format_value

    async def process_request(self, request: Request):
        return self.get_fluent(request.headers.get("accept-language", FALLBACK_LOCALE))

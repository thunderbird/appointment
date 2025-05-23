from typing import Union, Dict, Any

from starlette_context import context, errors
from .middleware.l10n import get_fluent


def l10n(msg_id: str, args: Union[Dict[str, Any], None] = None, lang: str = None) -> str:
    """Helper function to automatically call fluent.format_value from context.
    If a lang parameter was given, no context to retrieve languages from is needed
    and the translation can be directly loaded
    """
    if lang:
        return get_fluent([lang])(msg_id, args)

    # Get locale from context
    try:
        if 'l10n' not in context:
            return msg_id
    except errors.ContextDoesNotExistError:
        return msg_id

    return context['l10n'](msg_id, args)

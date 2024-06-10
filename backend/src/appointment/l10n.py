from typing import Union, Dict, Any

from starlette_context import context, errors


def l10n(msg_id: str, args: Union[Dict[str, Any], None] = None) -> str:
    """Helper function to automatically call fluent.format_value from context"""
    try:
        if 'l10n' not in context:
            return msg_id
    except errors.ContextDoesNotExistError:
        return msg_id

    return context['l10n'](msg_id, args)

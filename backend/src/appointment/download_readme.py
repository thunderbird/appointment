import datetime

from .l10n import l10n


def get_download_readme():
    """Returns the localized download readme"""
    return l10n('account-data-readme', {'download_time': datetime.datetime.now(datetime.UTC)})

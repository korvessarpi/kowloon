# --- Django 4+ i18n compat shim for legacy imports ---------------------------
# Some third-party / legacy modules still use:
#   ugettext, ugettext_lazy, ungettext, ungettext_lazy, ugettext_noop
# These were removed in Django ≥4. We alias them to the modern gettext API.
from django.utils import translation as _translation  # this is the module object

# Only alias if the old names are missing
if not hasattr(_translation, "ugettext"):
    from django.utils.translation import (
        gettext, gettext_lazy,
        ngettext, ngettext_lazy,
        gettext_noop,  # available as a no-op marker
    )
    _translation.ugettext = gettext
    _translation.ugettext_lazy = gettext_lazy
    _translation.ungettext = ngettext
    _translation.ungettext_lazy = ngettext_lazy
    _translation.ugettext_noop = gettext_noop
# --- end compat shim ----------------------------------------------------------

# Import your base settings AFTER the shim so import-time i18n users are patched.
from .settings import *

# -------------------------- Production overrides -----------------------------
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "::1", "*"]  # tighten in real prod

# Keep DATABASES from base; Docker/env should supply credentials.

# Helpdesk / API config (via env)
import os
REQUEST_QUEUE_SLUG = os.environ.get("REQUEST_QUEUE_SLUG", "")
REQUEST_API_URL    = os.environ.get("REQUEST_API_URL", "")
REQUEST_API_TOKEN  = (
    os.environ.get("REQUEST_API_TOKEN")
    or os.environ.get("REQUEST_API_KEY")
    or ""
)


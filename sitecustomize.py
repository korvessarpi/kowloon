try:
    from django.utils import translation as _t
    from django.utils.translation import (
        gettext as _gettext,
        ngettext as _ngettext,
        gettext_lazy as _gettext_lazy,
        ngettext_lazy as _ngettext_lazy,
    )
    _t.ugettext = getattr(_t, "ugettext", _gettext)
    _t.ungettext = getattr(_t, "ungettext", _ngettext)
    _t.ugettext_lazy = getattr(_t, "ugettext_lazy", _gettext_lazy)
    _t.ungettext_lazy = getattr(_t, "ungettext_lazy", _ngettext_lazy)
except Exception:
    pass

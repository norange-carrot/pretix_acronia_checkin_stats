from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_acronia_checkin_view"
    verbose_name = "Pretix Acronia Checkin View"

    class PretixPluginMeta:
        name = gettext_lazy("Pretix Acronia Checkin View")
        author = "Nora Küchler"
        description = gettext_lazy(
            "Pretix plugin to create an extra view to check helper add-on check-ins"
        )
        visible = True
        version = __version__
        category = "FEATURE"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA

__version__ = "1.0.0"

default_app_config = "pretix_acronia_checkin_view.apps.PluginApp"

# Export PretixPluginMeta for plugin registration
try:
    from .apps import PluginApp

    PretixPluginMeta = PluginApp.PretixPluginMeta
except ImportError:
    pass

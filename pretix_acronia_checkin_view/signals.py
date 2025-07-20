from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from pretix.control.signals import nav_event


@receiver(nav_event, dispatch_uid="acronia_checkin_view_nav")
def add_checkin_stats_navigation(sender, request=None, **kwargs):
    """Add navigation entry for checkin statistics in the event control panel."""
    if not request.user.has_event_permission(
        request.organizer, request.event, "can_view_orders"
    ):
        return []

    url = resolve(request.path_info)
    is_active = (
        url.namespace == "plugins:pretix_acronia_checkin_view"
        and url.url_name == "checkin_stats"
    )

    return [
        {
            "label": _("Check-in Helper Statistics"),
            "url": reverse(
                "plugins:pretix_acronia_checkin_view:checkin_stats",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "parent": reverse(
                "control:event.orders.checkinlists",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": is_active,
            "icon": "fa-bar-chart",
        }
    ]

from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from pretix.control.signals import nav_event


@receiver(nav_event, dispatch_uid="acronia_checkin_view_nav")
def control_nav_import(sender, request=None, **kwargs):
    """
    Add navigation entry for checkin statistics in the event control panel.
    """
    url = resolve(request.path_info)
    if not request.user.has_event_permission(request.organizer, request.event, 'can_view_orders'):
        return []
    
    return [
        {
            'label': _('Check-in Statistics'),
            'url': reverse('plugins:pretix_acronia_checkin_view:checkin_stats', kwargs={
                'event': request.event.slug,
                'organizer': request.organizer.slug,
            }),
            'active': (url.namespace == 'plugins:pretix_acronia_checkin_view' and
                      url.url_name == 'checkin_stats'),
            'icon': 'fa-bar-chart',
        }
    ]

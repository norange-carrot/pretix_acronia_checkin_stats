# URLs for the pretix plugin
from django.urls import include, path

from . import urls

urlpatterns = [
    path('', include(urls, namespace='pretix_acronia_checkin_view')),
]

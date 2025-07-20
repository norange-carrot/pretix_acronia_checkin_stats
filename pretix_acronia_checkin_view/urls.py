from django.urls import path

from . import views

app_name = "pretix_acronia_checkin_view"

urlpatterns = [
    path(
        "control/event/<str:organizer>/<str:event>/checkins/stats/",
        views.CheckinStatsView.as_view(),
        name="checkin_stats",
    ),
]

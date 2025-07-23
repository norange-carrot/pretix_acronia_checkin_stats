import csv
from django.db.models import Count, F, Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from pretix.base.models import CheckinList, OrderPosition
from pretix.control.views.event import EventPermissionRequiredMixin


class CheckinStatsView(EventPermissionRequiredMixin, ListView):
    """View to display checkin statistics for helper addon products."""

    CHECKIN_LIST_ID = 17
    ADDON_PRODUCT_IDS = [624, 572]

    template_name = "pretix_acronia_checkin_view/checkin_stats.html"
    context_object_name = "stats"
    permission = "can_view_orders"
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        """Handle GET requests, including CSV export."""
        if request.GET.get("export") == "csv":
            return self.export_csv()
        return super().get(request, *args, **kwargs)

    def _get_csv_headers(self):
        """Get CSV headers for export."""
        return [
            _("Order Code"),
            _("Product"),
            _("Variation"),
            _("Attendee Name"),
            _("Email"),
            _("Booked Addons"),
            _("Check-ins"),
            _("Missing Helper Duties"),
        ]

    def _get_csv_row_data(self, position):
        """Get CSV row data for a position."""
        return [
            position.order.code,
            position.item.name,
            position.variation.value if position.variation else "",
            position.attendee_name or "",
            position.attendee_email or "",
            position.addon_count,
            position.checkin_count,
            position.missing_duties,
        ]

    def export_csv(self):
        """Export the current filtered data as CSV."""
        # Get all data without pagination for export
        original_paginate_by = self.paginate_by
        self.paginate_by = None
        queryset = self.get_queryset()
        self.paginate_by = original_paginate_by

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="checkin_helper_statistics_{self.request.event.slug}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(self._get_csv_headers())

        # Write data
        for position in queryset:
            writer.writerow(self._get_csv_row_data(position))

        return response

    def _get_checkin_list(self):
        """Get the checkin list for this view."""
        try:
            return CheckinList.objects.get(
                id=self.CHECKIN_LIST_ID, event=self.request.event
            )
        except CheckinList.DoesNotExist:
            return None

    def _get_base_queryset(self, checkin_list):
        """Get the base queryset for order positions."""
        return (
            OrderPosition.objects.filter(
                order__event=self.request.event,
                order__status__in=checkin_list.include_pending and ["p", "n"] or ["p"],
                item__in=(
                    checkin_list.limit_products.all()
                    if checkin_list.limit_products.exists()
                    else self.request.event.items.all()
                ),
            )
            .select_related("item", "variation", "order")
            .prefetch_related("all_checkins", "addons")
            .annotate(
                checkin_count=Count(
                    "all_checkins",
                    filter=Q(all_checkins__list_id=self.CHECKIN_LIST_ID),
                    distinct=True,
                ),
                addon_count=Count(
                    "addons",
                    filter=Q(addons__item_id__in=self.ADDON_PRODUCT_IDS),
                    distinct=True,
                ),
                missing_duties=F("addon_count") - F("checkin_count"),
            )
            .order_by("-missing_duties", "order__code")
        )

    def _apply_search_filter(self, queryset, search):
        """Apply search filter to queryset."""
        return queryset.filter(
            Q(order__code__icontains=search)
            | Q(attendee_name_cached__icontains=search)
            | Q(attendee_email__icontains=search)
            | Q(item__name__icontains=search)
        )

    def _apply_missing_filter(self, queryset, missing_filter):
        """Apply missing duties filter to queryset."""
        filters = {
            "missing": Q(missing_duties__gt=0),
            "complete": Q(missing_duties=0),
            "extra": Q(missing_duties__lt=0),
        }
        if missing_filter in filters:
            return queryset.filter(filters[missing_filter])
        return queryset

    def _apply_checkin_filter(self, queryset, checkin_filter):
        """Apply check-in status filter to queryset."""
        filters = {
            "none": Q(checkin_count=0),
            "at_least_one": Q(checkin_count__gt=0),
        }
        if checkin_filter in filters:
            return queryset.filter(filters[checkin_filter])
        return queryset

    def get_queryset(self):
        """Get filtered queryset for order positions."""
        checkin_list = self._get_checkin_list()
        if not checkin_list:
            return OrderPosition.objects.none()

        queryset = self._get_base_queryset(checkin_list)

        # Apply filters
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = self._apply_search_filter(queryset, search)

        missing_filter = self.request.GET.get("missing_filter", "")
        queryset = self._apply_missing_filter(queryset, missing_filter)

        checkin_filter = self.request.GET.get("checkin_filter", "")
        queryset = self._apply_checkin_filter(queryset, checkin_filter)

        return queryset

    def _calculate_statistics(self, all_positions):
        """Calculate statistics from all positions."""
        total_positions = all_positions.count()
        total_checkins = sum(pos.checkin_count for pos in all_positions)

        # Statistics for helper duties
        completed_duties = all_positions.filter(missing_duties__lte=0).count()
        missing_duties = all_positions.filter(missing_duties__gt=0).count()

        return {
            "total_positions": total_positions,
            "total_checkins": total_checkins,
            "completed_duties": completed_duties,
            "missing_duties": missing_duties,
        }

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)

        # Calculate statistics for all matching positions (not just current page)
        all_positions = self.get_queryset()
        statistics = self._calculate_statistics(all_positions)

        context.update(
            {
                **statistics,
                "event": self.request.event,
                "search_query": self.request.GET.get("search", ""),
                "missing_filter": self.request.GET.get("missing_filter", ""),
                "checkin_filter": self.request.GET.get("checkin_filter", ""),
            }
        )

        return context

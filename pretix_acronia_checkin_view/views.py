import csv
from django.db.models import Count, F, Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from pretix.base.models import OrderPosition
from pretix.control.views.event import EventPermissionRequiredMixin


class CheckinStatsView(EventPermissionRequiredMixin, ListView):
    """
    View to display checkin statistics per person.
    Shows the number of checkins for each order position/person.
    """

    template_name = "pretix_acronia_checkin_view/checkin_stats.html"
    context_object_name = "stats"
    permission = "can_view_orders"
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        """Handle GET requests, including CSV export."""
        if request.GET.get("export") == "csv":
            return self.export_csv()
        return super().get(request, *args, **kwargs)

    def export_csv(self):
        """Export the current filtered data as CSV."""
        # Get all data without pagination for export
        original_paginate_by = self.paginate_by
        self.paginate_by = None

        queryset = self.get_queryset()

        # Restore pagination
        self.paginate_by = original_paginate_by

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="checkin_helper_statistics_{self.request.event.slug}.csv"'
        )

        writer = csv.writer(response)

        # Write headers
        writer.writerow(
            [
                _("Order Code"),
                _("Product"),
                _("Variation"),
                _("Attendee Name"),
                _("Email"),
                _("Booked Addons"),
                _("Check-ins"),
                _("Missing Helper Duties"),
            ]
        )

        # Write data
        for position in queryset:
            writer.writerow(
                [
                    position.order.code,
                    position.item.name,
                    position.variation.value if position.variation else "",
                    position.attendee_name or "",
                    position.attendee_email or "",
                    position.addon_count,
                    position.checkin_count,
                    position.missing_duties,
                ]
            )

        return response

    def get_queryset(self):
        # Get all order positions for this event that are eligible for checkin-list with ID 3
        # Show all positions regardless of check-in status
        from pretix.base.models import CheckinList

        try:
            checkin_list = CheckinList.objects.get(id=3, event=self.request.event)
        except CheckinList.DoesNotExist:
            # If checkin list doesn't exist, return empty queryset
            return OrderPosition.objects.none()

        # Get all positions that match the checkin list criteria
        queryset = (
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
                    "all_checkins", filter=Q(all_checkins__list_id=3), distinct=True
                ),
                addon_count=Count(
                    "addons", filter=Q(addons__item_id__in=[4, 7]), distinct=True
                ),
                missing_duties=F("addon_count") - F("checkin_count"),
            )
            .order_by("-missing_duties", "order__code")
        )

        # Filter by search query if provided
        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(order__code__icontains=search)
                | Q(attendee_name_cached__icontains=search)
                | Q(attendee_email__icontains=search)
                | Q(item__name__icontains=search)
            )

        # Filter by missing duties status
        missing_filter = self.request.GET.get("missing_filter", "")
        if missing_filter == "missing":
            queryset = queryset.filter(missing_duties__gt=0)
        elif missing_filter == "complete":
            queryset = queryset.filter(missing_duties=0)
        elif missing_filter == "extra":
            queryset = queryset.filter(missing_duties__lt=0)

        # Filter by check-in status
        checkin_filter = self.request.GET.get("checkin_filter", "")
        if checkin_filter == "none":
            queryset = queryset.filter(checkin_count=0)
        elif checkin_filter == "at_least_one":
            queryset = queryset.filter(checkin_count__gt=0)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate statistics for all matching positions (not just current page)
        all_positions = self.get_queryset()
        total_positions = all_positions.count()

        # Calculate total checkins
        total_checkins = sum(pos.checkin_count for pos in all_positions)

        # Find positions with multiple checkins
        multiple_checkins = all_positions.filter(checkin_count__gt=1).count()

        context.update(
            {
                "total_positions": total_positions,
                "total_checkins": total_checkins,
                "multiple_checkins": multiple_checkins,
                "event": self.request.event,
                "search_query": self.request.GET.get("search", ""),
                "missing_filter": self.request.GET.get("missing_filter", ""),
                "checkin_filter": self.request.GET.get("checkin_filter", ""),
            }
        )

        return context

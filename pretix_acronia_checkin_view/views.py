from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from pretix.base.models import Checkin, OrderPosition
from pretix.control.views.event import EventPermissionRequiredMixin


class CheckinStatsView(EventPermissionRequiredMixin, ListView):
    """
    View to display checkin statistics per person.
    Shows the number of checkins for each order position/person.
    """
    template_name = 'pretix_acronia_checkin_view/checkin_stats.html'
    context_object_name = 'stats'
    permission = 'can_view_orders'
    paginate_by = 50
    
    def get_queryset(self):
        # Get all order positions for this event that have at least one checkin
        # and annotate with checkin count
        queryset = OrderPosition.objects.filter(
            order__event=self.request.event,
            all_checkins__isnull=False
        ).select_related(
            'item', 'variation', 'order'
        ).prefetch_related(
            'all_checkins'
        ).annotate(
            checkin_count=Count('all_checkins', distinct=True)
        ).order_by('-checkin_count', 'order__code', 'positionid')
        
        # Filter by search query if provided
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(order__code__icontains=search) |
                Q(attendee_name__icontains=search) |
                Q(attendee_email__icontains=search) |
                Q(item__name__icontains=search)
            )
        
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
        
        context.update({
            'total_positions': total_positions,
            'total_checkins': total_checkins,
            'multiple_checkins': multiple_checkins,
            'event': self.request.event,
            'search_query': self.request.GET.get('search', ''),
        })
        
        return context

from django.urls import path
from .views import CategoryViewSet, DashboardView, PublicCategoryListView, PublicTicketView, RegisterView, LoginView, MeView, RequestPasswordReset, ConfirmPasswordReset, TicketSalesListView, TicketViewSet, UpdateUserView
from .views import (
    PublicEventListView,
    PublicCandidateListView,
    EventResultsView,
)
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, CandidateViewSet


app_name = "core"

router = DefaultRouter()
router.register(r'organizer/events', EventViewSet, basename='organizer-events')
router.register(r'organizer/categories', CategoryViewSet, basename='organizer-categories')
router.register(r'organizer/candidates', CandidateViewSet, basename='organizer-candidates')
router.register(r'organizer/tickets', TicketViewSet, basename='organizer-tickets')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/update/', UpdateUserView.as_view(), name='update-user'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/request-password-reset/', RequestPasswordReset.as_view(), name='request-password-reset'),
    path('auth/confirm-password-reset/', ConfirmPasswordReset.as_view(), name='confirm-password-reset'),
]

urlpatterns += [
    path('dashboard', DashboardView.as_view(), name='dashboard'),
    path('organizer/tickets/sales', TicketSalesListView.as_view(), name='ticket-sales'),
    
]

urlpatterns += [
    path('public/events/', PublicEventListView.as_view(), name='public-events'),
    path('public/events/<str:shortcode>/categories/', PublicCategoryListView.as_view(), name='public-categories'),
    path('public/events/candidates/', PublicCandidateListView.as_view(), name='public-candidates'),
    path('public/events/<str:shortcode>/results/', EventResultsView.as_view(), name='public-results'),
    path('events/<int:event_id>/tickets/', PublicTicketView.as_view(), name='public-event-tickets'),
]

urlpatterns += router.urls

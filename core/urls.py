from django.urls import path
from .views import CategoryViewSet, RegisterView, LoginView, MeView, RequestPasswordReset, ConfirmPasswordReset, UpdateUserView
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

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/update/', UpdateUserView.as_view(), name='update-user'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/request-password-reset/', RequestPasswordReset.as_view(), name='request-password-reset'),
    path('auth/confirm-password-reset/', ConfirmPasswordReset.as_view(), name='confirm-password-reset'),
]

urlpatterns += [
    path('public/events/', PublicEventListView.as_view(), name='public-events'),
    path('public/events/<str:shortcode>/categories/', PublicCandidateListView.as_view(), name='public-candidates'),
    path('public/events/candidates/', PublicCandidateListView.as_view(), name='public-candidates'),
    path('public/events/<str:shortcode>/results/', EventResultsView.as_view(), name='public-results'),
]

urlpatterns += router.urls

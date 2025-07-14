from django.urls import path
from tally.views import PublicEventResultsView

app_name = "tally"

urlpatterns = [
    path('results/<str:shortcode>/', PublicEventResultsView.as_view(), name='public-results'),
]

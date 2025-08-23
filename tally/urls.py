from django.urls import path
from tally.views import EventResultsView

app_name = "tally"

urlpatterns = [
    path('results', EventResultsView.as_view(), name='public-results'),
]

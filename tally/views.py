from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Candidate
from core.models import Event
from tally.serializers import PublicCandidateResultSerializer
from django.shortcuts import get_object_or_404
from core.mixins.response import StandardResponseView

class PublicEventResultsView(StandardResponseView):
    permission_classes = [AllowAny]

    def get(self, request, shortcode):
        event = get_object_or_404(Event, shortcode=shortcode, is_active=True, is_blocked=False)
        candidates = Candidate.objects.filter(event=event, is_blocked=False)

        serializer = PublicCandidateResultSerializer(candidates, many=True)
        return Response({
            "event": event.name,
            "shortcode": event.shortcode,
            "results": serializer.data
        })

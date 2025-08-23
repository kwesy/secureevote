from django.shortcuts import render

# Create your views here.
from core.models.category import Category
from core.permissions import IsOrganizer
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from tally.serializers import CategoryResultSerializer
from django.shortcuts import get_object_or_404
from core.mixins.response import StandardResponseView
from rest_framework import status

class EventResultsView(StandardResponseView):
    permission_classes = [IsOrganizer]

    def get(self, request):
        event_id = request.query_params.get('event')
        category_id = request.query_params.get('category')

        category = get_object_or_404(Category, id=category_id, event_id=event_id, event__user=request.user)
        serializer = CategoryResultSerializer(instance=category)

        return Response(serializer.data, status=status.HTTP_200_OK)

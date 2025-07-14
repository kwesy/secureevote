from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from .models.user import User
from .serializers import UserSerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        required_fields = ['email', 'password', 'organization_name']

        for field in required_fields:
            if field not in data:
                return Response({field: 'This field is required.'}, status=400)

        if User.objects.filter(email=data['email']).exists():
            return Response({'email': 'User with this email already exists.'}, status=400)

        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            organization_name=data['organization_name']
        )
        return Response(UserSerializer(user).data, status=201)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({'detail': 'Invalid credentials'}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    
class UpdateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        data = request.data
        
        if 'organization_name' in data:
            user.organization_name = data['organization_name']
        
        user.save()
        return Response(UserSerializer(user).data)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


#Password Reset via Token (Simple Version)
#For now, assume we send the reset link manually (or via a separate email service).


from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

class RequestPasswordReset(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            return Response({
                "uid": user.pk,
                "token": token
            })
        return Response({'detail': 'User not found'}, status=404)

class ConfirmPasswordReset(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            user = get_user_model().objects.get(pk=uid)
            if not default_token_generator.check_token(user, token):
                return Response({'detail': 'Invalid token'}, status=400)

            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password reset successful'})
        except Exception:
            return Response({'detail': 'Invalid request'}, status=400)


# Public APIs
# This section contains views that are accessible without authentication, allowing users to view events and candidates.
from .models.event import Event
from .models.candidate import Candidate
from .serializers import EventSerializer, CandidateSerializer
from rest_framework import generics

class PublicEventListView(generics.ListAPIView):
    queryset = Event.objects.filter(is_active=True, is_blocked=False)
    serializer_class = EventSerializer
    permission_classes = []

class PublicCandidateListView(generics.ListAPIView):
    serializer_class = CandidateSerializer
    permission_classes = []

    def get_queryset(self):
        return Candidate.objects.filter(
            event__shortcode=self.kwargs['shortcode'],
            is_blocked=False,
            event__is_active=True
        )

class EventResultsView(APIView):
    permission_classes = []

    def get(self, request, shortcode):
        event = Event.objects.filter(shortcode=shortcode, is_active=True).first()
        if not event:
            return Response({'detail': 'Event not found'}, status=404)

        candidates = Candidate.objects.filter(event=event)
        data = [
            {
                "candidate": c.name,
                "vote_count": c.vote_count
            }
            for c in candidates
        ]
        return Response({
            "event": event.name,
            "shortcode": event.shortcode,
            "results": data
        })


# Organizer role APIs
from rest_framework import viewsets
from .permissions import IsOrganizer

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CandidateViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        # Only return candidates for an event owned by the user
        # event_id = self.request.query_params.get('event_id')

        # if not event_id:
        #     # If no event_id is provided, return an empty queryset
        #     return Candidate.objects.none()
        
        return Candidate.objects.filter( event__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the event belongs to the authenticated user
        event = serializer.validated_data.get('event')
        if event.user != self.request.user:
            raise PermissionDenied("You do not have permission to add candidates to this event.")
        
        serializer.save()
from core.models.otp import OTP, generate_secure_otp
from core.models.ticket import Ticket, TicketSale
from rest_framework import status, permissions, filters, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotFound, ValidationError, AuthenticationFailed
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied

from services.services import send_email
from .models.user import User
from .serializers import OTPSerializer, PublicCandidateSerializer, PublicCategorySerializer, PublicEventSerializer, PublicTicketSerializer, ResendOTPSerializer, TicketSaleSerializer, TicketSerializer, UserSerializer
from .mixins.response import StandardResponseView
import logging

logger = logging.getLogger("error")

class RegisterView(StandardResponseView):
    permission_classes = [permissions.AllowAny]
    success_message = "User registered successfully"

    def post(self, request):
        data = request.data
        required_fields = ['email', 'password', 'organization_name']

        for field in required_fields:
            if field not in data:
                raise ValidationError({"detial": f'{field}: This field is required.'})

        if User.objects.filter(email=data['email']).exists():
            raise ValidationError({'detail': 'User with this email already exists.'})

        otp = OTP.objects.create(is_verified=False)
        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            organization_name=data['organization_name'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            otp = otp
        )

        # Send OTP to email
        try:
            send_email(
                subject="SecureEVote Signup Verification",
                template_name="emails/email_verification.html",
                context={"organization_name": user.organization_name, "otp_code": otp.code},
                recipient_list=[user.email],
            )
            send_email(
                subject="Welcome to SecureEVote 🎉",
                template_name="emails/welcome.html",
                context={
                    "organizer_name": user.organization_name,
                    "dashboard_url": "https://secureevote.com/dashboard",
                    "year": 2025,
                },
                recipient_list=[user.email],
            )
            
        except Exception as e:
            user.delete()
            logger.error(f"Error sending OTP email: {e}", exc_info=True)
            raise ValidationError({'detail': 'Failed to send OTP email. Please try again later.'})
        
        return Response({'email': user.email, 'request_id': otp.request_id}, status=201)
    
# Email OTP confirmation view
class EmailOTPVerificationView(StandardResponseView, generics.CreateAPIView):
    serializer_class = OTPSerializer
    permission_classes = []

    def post(self, request):
        self.success_message = "OTP confirmed successfully"
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        email = serializer.validated_data.get('id')
        code = serializer.validated_data.get('code')
        request_id = serializer.validated_data.get('request_id') # only used for resending OTP

        try:
            user = get_user_model().objects.get(email=email)

            # Verify the OTP code
            if user and not user.is_verified and user.otp.verify(code):
                user.is_verified = True
                user.save()
                return Response({"detail": "OTP confirmed successfully"}, status=status.HTTP_200_OK)
            else:
                raise ValidationError({"detail": "Invalid OTP code or Expired"})
            
        except get_user_model().DoesNotExist:
            return NotFound({"detail": "User not found"})
        
#Unauthenticated OTP Resend View
class ResendOTPView(StandardResponseView):
    permission_classes = []
    serializer_class = ResendOTPSerializer

    def post(self, request):
        self.success_message = "OTP resent successfully."
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            raise ValidationError({'detail': serializer.errors})
        
        request_id = serializer.validated_data.get('id')
        otp = get_object_or_404(OTP, request_id=request_id, is_verified=False, )
        otp.code = generate_secure_otp(6)
        otp.save()

        #TODO: Integrate with SMS service to send the OTP code to the user's email or phone number
        return Response(status=status.HTTP_205_RESET_CONTENT)

class LoginView( StandardResponseView):
    permission_classes = [permissions.AllowAny]
    success_message = "User logged in successfully"

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if not user:
            raise AuthenticationFailed({'detail': 'Invalid credentials'})
        
        if not user.is_verified:
            raise PermissionDenied("Please verify your account to continue.")

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })

class LogoutView(StandardResponseView):
    permission_classes = [permissions.IsAuthenticated]
    success_message = "User logged out successfully"
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            raise ValidationError({'detail': 'Invalid token'})  
    
class UpdateUserView(StandardResponseView):
    permission_classes = [permissions.IsAuthenticated]
    success_message = "User updated successfully"

    def patch(self, request):
        user = request.user
        data = request.data
        
        if 'organization_name' in data:
            user.organization_name = data['organization_name']
        
        user.save()
        return Response(UserSerializer(user).data)

class MeView(StandardResponseView):
    permission_classes = [permissions.IsAuthenticated]
    success_message = {"GET": "User details fetched successfully"}

    def get(self, request):
        return Response(UserSerializer(request.user).data)


#Password Reset via Token (Simple Version)
#For now, assume we send the reset link manually (or via a separate email service).


from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

class RequestPasswordReset(StandardResponseView):
    permission_classes = [permissions.AllowAny]
    success_message = {"POST": "Password reset token generated successfully"}

    def post(self, request):
        email = request.data.get('email')
        user = get_user_model().objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            return Response({
                "uid": user.pk,
                "token": token
            })
        raise NotFound({'detail': 'User not found'})

class ConfirmPasswordReset(StandardResponseView):
    permission_classes = [permissions.AllowAny]
    # success_message = "Password reset successful"

    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            user = get_user_model().objects.get(pk=uid)
            if not default_token_generator.check_token(user, token):
                raise ValidationError({'detail': 'Invalid token'})

            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password reset successful'}, status=200)
        except Exception:
            raise ValidationError({'detail': 'Invalid request'})


# Public APIs
# This section contains views that are accessible without authentication, allowing users to view events and candidates.
from .models.event import Event
from .models.candidate import Candidate
from .models.category import Category
from .serializers import EventSerializer, CandidateSerializer, CategorySerializer
from rest_framework import generics

class PublicEventListView(StandardResponseView, generics.ListAPIView):
    queryset = Event.objects.filter(is_active=True, is_blocked=False)
    serializer_class = PublicEventSerializer
    permission_classes = []
    success_message = "Events fetched successfully"

class PublicCategoryListView(StandardResponseView, generics.ListAPIView):
    serializer_class = PublicCategorySerializer
    permission_classes = [permissions.AllowAny]
    success_message = "Categories fetched successfully"

    def get_queryset(self):
        return Category.objects.filter(
            event__shortcode=self.kwargs['shortcode'],
            event__is_active=True,
            is_active=True
        )

class PublicCandidateListView(StandardResponseView, generics.ListAPIView):
    serializer_class = PublicCandidateSerializer
    permission_classes = []
    success_message = "Candidates fetched successfully"

    def get_queryset(self):

        shortcode = self.request.query_params.get("eventcode")
        category = self.request.query_params.get("category")

        if not shortcode or not category:
            return Candidate.objects.none()

        return Candidate.objects.filter(
            event__shortcode=shortcode,
            category=category,
            is_blocked=False,
            event__is_active=True
        )

class EventResultsView(StandardResponseView):
    permission_classes = []
    success_message = "Event results fetched successfully"

    def get(self, request, shortcode):
        event = Event.objects.filter(shortcode=shortcode, is_active=True).first()
        if not event:
            raise NotFound({'detail': 'Event not found'})

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
    
class PublicTicketView(StandardResponseView, generics.ListAPIView, generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicTicketSerializer
    success_message = "Ticket details fetched successfully"

    def get_queryset(self):
        event = self.kwargs.get('event_id') 

        if not event:
            return Ticket.objects.none()
        queryset = Ticket.objects.filter(event=event, is_active=True)
        return queryset


# Organizer role APIs
from rest_framework import viewsets
from .permissions import IsOrganizer

class EventViewSet(StandardResponseView, viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(StandardResponseView, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        # Only return category owned by the user
        return Category.objects.filter( event__user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        # Override list to return categories for a specific event
        event_id = self.request.query_params.get('event')

        if not event_id:
            # If no event_id is provided, return an empty queryset
            queryset = Category.objects.none()
        else:
            # Filter categories by the provided event_id
            queryset = self.get_queryset().filter(event_id=event_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        # Ensure the event belongs to the authenticated user
        event = serializer.validated_data.get('event')
        if event.user != self.request.user:
            raise PermissionDenied("You do not have permission to add category to this event.")
        
        serializer.save()

class CandidateViewSet(StandardResponseView, viewsets.ModelViewSet):
    serializer_class = CandidateSerializer
    permission_classes = [IsOrganizer]

    def get_queryset(self):
        # Only return candidates owned by the user
        return Candidate.objects.filter( category__event__user=self.request.user)

    def perform_create(self, serializer):
        print(serializer.validated_data)
        # Ensure the event belongs to the authenticated user
        event = serializer.validated_data.get('event')
        category = serializer.validated_data.get('category')
        if event.user != self.request.user:
            raise PermissionDenied("You do not have permission to add candidates to this event.")
        
        if category.event.user != self.request.user:
            raise PermissionDenied("You do not have permission to add candidates to this category.")
        
        # Save the candidate with the authenticated user as the organizer
        serializer.save()

    def list(self, request, *args, **kwargs):
        # Override list to return candidates for a specific event or category
        category_id = self.request.query_params.get('category')

        if not category_id:
            # If no filters are provided, return an empty queryset
            queryset = Candidate.objects.none()
        else:
            # Filter candidates by the provided event_id and/or category_id
            queryset = self.get_queryset()
            queryset = queryset.filter(category_id=category_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_update(self, serializer):
        # Ensure the event and category belong to the authenticated user
        event = serializer.validated_data.get('event')
        category = serializer.validated_data.get('category')
        if not event or not category:
            raise PermissionDenied("Event and category must be specified for updating candidates.")
        
        if event.user != self.request.user:
            raise PermissionDenied("You do not have permission to update candidates for this event.")
        
        if category.event.user != self.request.user:
            raise PermissionDenied("You do not have permission to update candidates for this category.")
        
        # Save the updated candidate
        serializer.save()

class TicketViewSet(StandardResponseView, viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsOrganizer]
    
    def get_queryset(self):
        return Ticket.objects.filter(event__user=self.request.user)
    
    def perform_create(self, serializer):
        # and Event has a user field that points to the organizer (self.request.user).
        event = serializer.validated_data.get('event')
        if event.user != self.request.user:
            raise PermissionDenied("You are not allowed create tickets this event.")
        
        serializer.save()

class TicketSalesListView(StandardResponseView, generics.ListAPIView):
    permission_classes = [IsOrganizer]
    serializer_class = TicketSaleSerializer
    success_message = "Ticket sales fetched successfully"
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'customer_name',
        'recipient_contact',
        'payment__phone_number',
        'ticket__type',
    ]

    def get_queryset(self):
        queryset = TicketSale.objects.filter(ticket__event__user=self.request.user)

        # Optional filters
        ticket_code = self.request.query_params.get('ticket')
        customer_name = self.request.query_params.get('customer_name')
        recipient_contact = self.request.query_params.get('recipient_contact')
        phone_number = self.request.query_params.get('phone_number')

        if ticket_code:
            queryset = queryset.filter(id__icontains=ticket_code)
        if customer_name:
            queryset = queryset.filter(customer_name__icontains=customer_name)
        if recipient_contact:
            queryset = queryset.filter(recipient_contact__icontains=recipient_contact)
        if phone_number:
            queryset = queryset.filter(phone_number__icontains=phone_number)

        return queryset
        
class DashboardView(StandardResponseView):
    permission_classes = [IsOrganizer]
    success_message = "Dashboard data fetched successfully"

    def get(self, request):
        user = request.user
        events = Event.objects.filter(user=user, is_active=True, is_blocked=False)

        data = {
            "total_active_events": events.count(),
            "active_events": EventSerializer(events, many=True).data,
            "available_balance": user.balance,
        }

        return Response(data)

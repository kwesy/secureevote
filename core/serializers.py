from rest_framework import serializers
from .models.user import User
from .models.event import Event
from .models.candidate import Candidate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'organization_name']

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'gender', 'photo', 'description', 'vote_count', 'is_blocked', 'event']

class EventSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'shortcode',
            'amount_per_vote', 'start_time', 'end_time',
            'is_active', 'is_blocked', 'candidates'
        ]

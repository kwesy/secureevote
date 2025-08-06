from rest_framework import serializers
from .models.user import User
from .models.event import Event
from .models.candidate import Candidate
from .models.category import Category

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'organization_name']

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'gender', 'photo', 'description', 'vote_count', 'is_blocked', 'event', 'category' ]
        read_only_fields = ['vote_count']

class CategorySerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "event", "name", "description", "is_active", "candidates"]

class EventSerializer(serializers.ModelSerializer):
    # candidates = CandidateSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'shortcode',
            'amount_per_vote', 'start_time', 'end_time',
            'is_active', 'is_blocked', 'categories'
        ]

from core.models.candidate import Candidate
from rest_framework import serializers


class PublicCandidateResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'photo', 'description', 'vote_count']

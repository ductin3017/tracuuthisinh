from rest_framework import serializers
from .models import Candidate, PersonalInfo

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['candidate_id', 'personal_info_id']

class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = ['personal_info_id', 'date_of_birth', 'name', 'identity_number', 'address', 'phone_number', 'email', 'gender']
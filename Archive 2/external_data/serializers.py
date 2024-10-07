# external_data/serializers.py
from rest_framework import serializers
from .models import ExternalLead
from django.contrib.auth import get_user_model

User = get_user_model()

class ExternalLeadSerializer(serializers.ModelSerializer):
    trainer_suggestions = serializers.SerializerMethodField()
    class Meta:
        model = ExternalLead
        fields = '__all__'
        read_only_fields = ('created_at', 'trainer_suggestions')
        
    def get_trainer_suggestions(self, obj):
        return self.context.get('trainer_suggestions', [])

    def validate_phone(self, value):
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Phone number must contain at least 10 digits.")
        return value

    def validate_duration(self, value):
        if value <= 0 or value > 480:  # 480 minutes = 8 hours
            raise serializers.ValidationError("Duration must be between 1 and 480 minutes.")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        slots = [data.get('slot_1'), data.get('slot_2'), data.get('slot_3')]
        non_null_slots = [slot for slot in slots if slot is not None]
        if len(set(non_null_slots)) != len(non_null_slots):
            raise serializers.ValidationError("All provided slots must be different times.")
        if not any(non_null_slots):
            raise serializers.ValidationError("At least one slot must be provided.")
        return data

class TrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class AvailabilitySerializer(serializers.Serializer):
    date = serializers.DateField()
    slots = serializers.ListField(child=serializers.TimeField())

class ConsolidatedTrainerSuggestionSerializer(serializers.Serializer):
    trainer = TrainerSerializer()
    availability = AvailabilitySerializer(many=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert availability list to a dictionary for easier frontend consumption
        availability_dict = {item['date']: item['slots'] for item in data['availability']}
        data['availability'] = availability_dict
        return data
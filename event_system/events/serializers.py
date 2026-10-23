from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Event, Registration


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class EventSerializer(serializers.ModelSerializer):
    seats_left = serializers.ReadOnlyField()
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'location',
            'date_time',
            'capacity',
            'seats_left',
            'created_by_username',
            'created_at',
        ]
        read_only_fields = ['created_at']


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'location',
            'date_time',
            'capacity',
        ]


class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='event.title')
    username = serializers.ReadOnlyField(source='user.username')
    event_detail = EventSerializer(source='event', read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id',
            'user',
            'username',
            'event',
            'event_title',
            'event_detail',
            'status',
            'registered_at',
        ]
        read_only_fields = ['user', 'registered_at']

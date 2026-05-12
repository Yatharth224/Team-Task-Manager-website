from rest_framework import serializers
from django.utils import timezone

from .models import Task
from accounts.serializers import BasicUserSerializer


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = BasicUserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    created_by = BasicUserSerializer(read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'project',
            'assigned_to', 'assigned_to_id',
            'created_by', 'status', 'priority',
            'due_date', 'is_overdue', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'project')

    def get_is_overdue(self, obj):
        return obj.is_overdue


class TaskCreateSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'assigned_to_id', 'status', 'priority', 'due_date')

    def validate_due_date(self, val):
        if val and val < timezone.now().date():
            raise serializers.ValidationError("Due date can't be in the past.")
        return val


class TaskUpdateSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ('title', 'description', 'assigned_to_id', 'status', 'priority', 'due_date')
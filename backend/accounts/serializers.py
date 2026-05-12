from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Project, ProjectMember
from accounts.serializers import BasicUserSerializer

User = get_user_model()


class MembershipSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ('id', 'user', 'role', 'joined_at')


class ProjectSerializer(serializers.ModelSerializer):
    owner = BasicUserSerializer(read_only=True)
    members = MembershipSerializer(source='memberships', many=True, read_only=True)
    my_role = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'owner', 'members', 'my_role', 'task_count', 'created_at')
        read_only_fields = ('id', 'owner', 'created_at')

    def get_my_role(self, obj):
        req_user = self.context['request'].user
        try:
            seat = obj.memberships.get(user=req_user)
            return seat.role
        except ProjectMember.DoesNotExist:
            return None

    def get_task_count(self, obj):
        return obj.task_set.count()


class AddMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=['admin', 'member'], default='member')

    def validate_email(self, val):
        try:
            User.objects.get(email=val)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")
        return val
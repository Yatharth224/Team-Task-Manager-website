from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Project, ProjectMember
from .serializers import ProjectSerializer, AddMemberSerializer
from .permissions import get_membership

User = get_user_model()


class ProjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # only return projects this user belongs to
        user_project_ids = ProjectMember.objects.filter(user=request.user).values_list('project_id', flat=True)
        all_projects = Project.objects.filter(id__in=user_project_ids).order_by('-created_at')
        data = ProjectSerializer(all_projects, many=True, context={'request': request}).data
        return Response(data)

    def post(self, request):
        form = ProjectSerializer(data=request.data, context={'request': request})
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        new_project = form.save(owner=request.user)

        # creator automatically becomes admin
        ProjectMember.objects.create(
            project=new_project,
            user=request.user,
            role=ProjectMember.ADMIN
        )

        return Response(ProjectSerializer(new_project, context={'request': request}).data, status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_project_for_member(self, pk, user):
        project = get_object_or_404(Project, pk=pk)
        seat = get_membership(project, user)
        if seat is None:
            return None, None
        return project, seat

    def get(self, request, pk):
        project, seat = self._get_project_for_member(pk, request.user)
        if project is None:
            return Response({'error': 'Not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProjectSerializer(project, context={'request': request}).data)

    def patch(self, request, pk):
        project, seat = self._get_project_for_member(pk, request.user)
        if project is None:
            return Response({'error': 'Not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        if seat.role != ProjectMember.ADMIN:
            return Response({'error': 'Only admins can edit project details'}, status=status.HTTP_403_FORBIDDEN)

        form = ProjectSerializer(project, data=request.data, partial=True, context={'request': request})
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        form.save()
        return Response(form.data)

    def delete(self, request, pk):
        project, seat = self._get_project_for_member(pk, request.user)
        if project is None:
            return Response({'error': 'Not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
        if project.owner != request.user:
            return Response({'error': 'Only the project owner can delete it'}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MemberManageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        seat = get_membership(project, request.user)
        if seat is None or seat.role != ProjectMember.ADMIN:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        form = AddMemberSerializer(data=request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        target_user = User.objects.get(email=form.validated_data['email'])
        chosen_role = form.validated_data['role']

        existing = get_membership(project, target_user)
        if existing:
            return Response({'error': 'User is already a member'}, status=status.HTTP_400_BAD_REQUEST)

        ProjectMember.objects.create(project=project, user=target_user, role=chosen_role)
        return Response({'message': f'{target_user.name} added as {chosen_role}'}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        seat = get_membership(project, request.user)
        if seat is None or seat.role != ProjectMember.ADMIN:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if str(request.user.id) == str(user_id):
            return Response({'error': "You can't remove yourself"}, status=status.HTTP_400_BAD_REQUEST)

        membership_to_remove = get_object_or_404(ProjectMember, project=project, user_id=user_id)
        membership_to_remove.delete()
        return Response({'message': 'Member removed'})
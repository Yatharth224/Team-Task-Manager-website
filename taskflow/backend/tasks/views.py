from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer
from projects.models import Project, ProjectMember
from projects.permissions import get_membership


class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        seat = get_membership(project, request.user)
        if seat is None:
            return Response({'error': 'Not a member of this project'}, status=status.HTTP_403_FORBIDDEN)

        qs = Task.objects.filter(project=project).select_related('assigned_to', 'created_by')

        # filter by status if passed
        filter_status = request.query_params.get('status')
        if filter_status:
            qs = qs.filter(status=filter_status)

        # filter by assignee
        filter_user = request.query_params.get('assigned_to')
        if filter_user:
            qs = qs.filter(assigned_to_id=filter_user)

        qs = qs.order_by('-created_at')
        return Response(TaskSerializer(qs, many=True).data)

    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        seat = get_membership(project, request.user)
        if seat is None:
            return Response({'error': 'Not a member of this project'}, status=status.HTTP_403_FORBIDDEN)
        if seat.role != ProjectMember.ADMIN:
            return Response({'error': 'Only admins can create tasks'}, status=status.HTTP_403_FORBIDDEN)

        form = TaskCreateSerializer(data=request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        # verify the assignee is a project member
        assignee_id = form.validated_data.pop('assigned_to_id', None)
        if assignee_id:
            is_member = ProjectMember.objects.filter(project=project, user_id=assignee_id).exists()
            if not is_member:
                return Response({'error': 'Assignee must be a project member'}, status=status.HTTP_400_BAD_REQUEST)

        new_task = form.save(project=project, created_by=request.user, assigned_to_id=assignee_id)
        return Response(TaskSerializer(new_task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _load_task(self, request, project_pk, task_pk):
        project = get_object_or_404(Project, pk=project_pk)
        seat = get_membership(project, request.user)
        if seat is None:
            return None, None, None
        task = get_object_or_404(Task, pk=task_pk, project=project)
        return project, seat, task

    def get(self, request, project_pk, task_pk):
        project, seat, task = self._load_task(request, project_pk, task_pk)
        if task is None:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TaskSerializer(task).data)

    def patch(self, request, project_pk, task_pk):
        project, seat, task = self._load_task(request, project_pk, task_pk)
        if task is None:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        is_admin = seat.role == ProjectMember.ADMIN
        is_assignee = task.assigned_to == request.user

        if not is_admin and not is_assignee:
            return Response({'error': 'You can only update tasks assigned to you'}, status=status.HTTP_403_FORBIDDEN)

        # members can only update status, admins can change everything
        if not is_admin:
            allowed_fields = {'status'}
            incoming = set(request.data.keys())
            blocked = incoming - allowed_fields
            if blocked:
                return Response({'error': f'Members can only update status, not: {blocked}'}, status=status.HTTP_403_FORBIDDEN)

        form = TaskUpdateSerializer(task, data=request.data, partial=True)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        assignee_id = form.validated_data.pop('assigned_to_id', None)
        if assignee_id is not None:
            if is_admin:
                is_member = ProjectMember.objects.filter(project=project, user_id=assignee_id).exists()
                if not is_member:
                    return Response({'error': 'Assignee must be a project member'}, status=status.HTTP_400_BAD_REQUEST)
                form.save(assigned_to_id=assignee_id)
            else:
                form.save()
        else:
            form.save()

        task.refresh_from_db()
        return Response(TaskSerializer(task).data)

    def delete(self, request, project_pk, task_pk):
        project, seat, task = self._load_task(request, project_pk, task_pk)
        if task is None:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        if seat.role != ProjectMember.ADMIN:
            return Response({'error': 'Only admins can delete tasks'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        seat = get_membership(project, request.user)
        if seat is None:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        all_tasks = Task.objects.filter(project=project)
        today = timezone.now().date()

        total = all_tasks.count()
        todo_count = all_tasks.filter(status=Task.TODO).count()
        in_progress_count = all_tasks.filter(status=Task.IN_PROGRESS).count()
        done_count = all_tasks.filter(status=Task.DONE).count()
        overdue_count = all_tasks.filter(due_date__lt=today).exclude(status=Task.DONE).count()

        # tasks per member
        per_user = []
        memberships = project.memberships.select_related('user')
        for m in memberships:
            per_user.append({
                'user': m.user.name,
                'email': m.user.email,
                'role': m.role,
                'assigned': all_tasks.filter(assigned_to=m.user).count(),
                'done': all_tasks.filter(assigned_to=m.user, status=Task.DONE).count(),
            })

        return Response({
            'total': total,
            'by_status': {
                'todo': todo_count,
                'in_progress': in_progress_count,
                'done': done_count,
            },
            'overdue': overdue_count,
            'per_member': per_user,
        })
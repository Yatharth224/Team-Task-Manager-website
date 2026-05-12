from django.db import models
from django.conf import settings
from projects.models import Project


class Task(models.Model):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'

    STATUS_CHOICES = [
        (TODO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (DONE, 'Done'),
    ]

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=TODO)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.due_date and self.status != self.DONE:
            return self.due_date < timezone.now().date()
        return False
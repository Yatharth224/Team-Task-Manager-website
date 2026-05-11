from django.urls import path
from . import views

urlpatterns = [
    path('<int:project_pk>/tasks/', views.TaskListView.as_view(), name='task-list'),
    path('<int:project_pk>/tasks/<int:task_pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:project_pk>/dashboard/', views.DashboardView.as_view(), name='dashboard'),
]

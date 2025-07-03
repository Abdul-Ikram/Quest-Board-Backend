from django.urls import path
from . import views

urlpatterns = [
    path('health-check/', views.HealthCheckView.as_view(), name='health_check'),
    path('task-upload/', views.TaskUploadView.as_view(), name='task_upload'),
    path('get-tasks/', views.GetTaskView.as_view(), name='get_user_tasks'),
    path('edit-task/<int:task_id>/', views.EditTaskView.as_view(), name='edit_task'),
    path('delete-task/<int:task_id>/', views.TaskDeleteView.as_view(), name='delete_task'),
    path('edit-profile/<int:pk>/', views.ProfileUpdateView.as_view(), name='edit-profile'),
    path('get-profile/', views.GetProfileView.as_view(), name='get-profile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
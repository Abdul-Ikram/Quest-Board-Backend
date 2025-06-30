from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import TaskUploadSerializer, GetTasksSerializer
from authentication.permissions import IsTasksmith, IsAdminOrOwner
from .models import TasksDetail
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Create your views here.

# Health Check View:
class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status_code': 200,
            'message': 'API running successfully!',
        }, status=status.HTTP_200_OK)

class TaskUploadView(APIView):
    permission_classes = [IsAuthenticated, IsTasksmith]

    def post(self, request):
        user = request.user
        if not user.phone_number:
            return Response({
                'status_code': 400,
                'message': 'Phone number is required to upload a task.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_verified:
            return Response({
                'status_code': 403,
                'message': 'Your account must be verified to upload tasks.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # serializer = TaskUploadSerializer(data=request.data)
        serializer = TaskUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                # demand_side=user.phone_number,
            )
            return Response({
                'status_code': 201,
                'message': 'Task uploaded successfully!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status_code': 400,
            'message': 'Task upload failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class GetTaskView(APIView):
    permission_classes = [IsAuthenticated, IsTasksmith]

    def get(self, request):
        tasks = TasksDetail.objects.filter(user=request.user, deleted_at__isnull=True)
        serializer = GetTasksSerializer(tasks, many=True)
        return Response({
            'status_code': 200,
            'message': 'Tasks fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

class EditTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        user = request.user
        task = get_object_or_404(TasksDetail, id=task_id, user=user, deleted_at__isnull=True)

        serializer = TaskUploadSerializer(task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status_code': 200,
                'message': 'Task updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'status_code': 400,
            'message': 'Update failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class TaskDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def delete(self, request, task_id):
        try:
            task = TasksDetail.objects.get(id=task_id, user=request.user, deleted_at__isnull=True)
        except TasksDetail.DoesNotExist:
            return Response({
                'status_code': 404,
                'message': 'Task not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        task.deleted_at = timezone.now()
        task.deleted_by = request.user.username
        task.save()

        return Response({
            'status_code': 200,
            'message': 'Task deleted successfully.',
            'data': {
                "task_deleted_by": task.deleted_by,
            }
        }, status=status.HTTP_200_OK)

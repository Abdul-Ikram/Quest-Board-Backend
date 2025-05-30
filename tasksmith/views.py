from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import TaskUploadSerializer
from authentication.permissions import IsTasksmith, IsAdminOrOwner
from .models import TasksDetail
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
        serializer = TaskUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                demand_side="00000000000",
                # demand_side=request.user.phone_number,
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

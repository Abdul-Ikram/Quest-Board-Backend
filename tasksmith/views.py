from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import TaskUploadSerializer, GetTasksSerializer, UserProfileSerializer 
from authentication.permissions import IsTasksmith, IsAdminOrOwner
from .models import TasksDetail
from authentication.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from authentication.helpers import upload_to_imagekit

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

class ProfileUpdateView(APIView):
    def put(self, request, pk, *args, **kwargs):
        try:
            # Retrieve the user
            user = get_object_or_404(User, id=pk)

            if request.user != user:
                return Response({
                    'success': False,
                    'message': 'You can only update your own profile.'
                }, status=status.HTTP_200_OK)

            full_name = request.data.get('full_name', user.username)
            bio = request.data.get('bio', user.bio)
            location = request.data.get('location', user.location)
            phone_number = request.data.get('phone_number', user.phone_number)
            website = request.data.get('website', user.website)
            company = request.data.get('website', user.company)
            image_file = request.FILES.get('image', user.image)

            if 'image' in request.FILES:
                image_file = request.FILES['image']
                user.image = upload_to_imagekit(image_file)
            elif request.data.get('image') == '':
                user.image = user.image
                
            user.full_name = full_name
            user.bio = bio
            user.location = location
            user.phone_number = phone_number
            user.website = website
            user.company = company
            user.save()

            return Response({
                'success': True,
                'message': 'User profile updated successfully.',
                'data': {
                    'user': {
                        'id': user.id, # type: ignore
                        'full_name': user.full_name,
                        'email': user.email,
                        'bio': user.bio,
                        'location': user.location,
                        'company': user.company,
                        'phone_number': user.phone_number,
                        'website': user.website,
                        'image': user.image,
                    }
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_200_OK)

class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response({
            'status_code': 200,
            'message': 'Profile retrieved successfully.',
            'data': {
                'user': serializer.data
            }
        }, status=status.HTTP_200_OK)

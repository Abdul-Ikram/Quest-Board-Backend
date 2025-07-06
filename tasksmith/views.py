from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import TaskUploadSerializer, GetTasksSerializer, UserProfileSerializer
from authentication.permissions import IsTasksmith, IsAdminOrOwner
from .models import TasksDetail
from authentication.models import User, Specialty
from django.shortcuts import get_object_or_404
from django.utils import timezone
from authentication.helpers import upload_to_imagekit
from django.db import models

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
    permission_classes = [IsAuthenticated, IsTasksmith]

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

# class ProfileUpdateView(APIView):
#     permission_classes = [IsAuthenticated, IsTasksmith]

#     def put(self, request, pk, *args, **kwargs):
#         try:
#             user = get_object_or_404(User, id=pk)

#             if request.user != user:
#                 return Response({
#                     'success': False,
#                     'message': 'You can only update your own profile.'
#                 }, status=status.HTTP_200_OK)

#             full_name = request.data.get('full_name', user.username)
#             bio = request.data.get('bio', user.bio)
#             location = request.data.get('location', user.location)
#             phone_number = request.data.get('phone_number', user.phone_number)
#             website = request.data.get('website', user.website)
#             company = request.data.get('website', user.company)
#             image_file = request.FILES.get('image', user.image)

#             if 'image' in request.FILES:
#                 image_file = request.FILES['image']
#                 user.image = upload_to_imagekit(image_file)
#             elif request.data.get('image') == '':
#                 user.image = user.image
                
#             user.full_name = full_name
#             user.bio = bio
#             user.location = location
#             user.phone_number = phone_number
#             user.website = website
#             user.company = company
#             user.save()

#             return Response({
#                 'success': True,
#                 'message': 'User profile updated successfully.',
#                 'data': {
#                     'user': {
#                         'id': user.id, # type: ignore
#                         'full_name': user.full_name,
#                         'email': user.email,
#                         'bio': user.bio,
#                         'location': user.location,
#                         'company': user.company,
#                         'phone_number': user.phone_number,
#                         'website': user.website,
#                         'image': user.image,
#                     }
#                 }
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': str(e)
#             }, status=status.HTTP_200_OK)

class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsTasksmith]

    def put(self, request, pk, *args, **kwargs):
        try:
            user = get_object_or_404(User, id=pk)

            if request.user != user:
                return Response({
                    'success': False,
                    'message': 'You can only update your own profile.'
                }, status=status.HTTP_403_FORBIDDEN)

            full_name = request.data.get('full_name', user.full_name)
            bio = request.data.get('bio', user.bio)
            location = request.data.get('location', user.location)
            phone_number = request.data.get('phone_number', user.phone_number)
            website = request.data.get('website', user.website)
            company = request.data.get('company', user.company)
            specialties_data = request.data.getlist('specialties', [])  # Expecting a list
            image_file = request.FILES.get('image', None)

            # Handle image upload
            if image_file:
                user.image = upload_to_imagekit(image_file)
            elif request.data.get('image') == '':
                user.image = None

            # Update basic fields
            user.full_name = full_name
            user.bio = bio
            user.location = location
            user.phone_number = phone_number
            user.website = website
            user.company = company

            user.save()

            if isinstance(specialties_data, list):
                new_specialties = []
                for specialty_name in specialties_data:
                    specialty_name = specialty_name.strip()
                    if specialty_name:
                        specialty_obj, _ = Specialty.objects.get_or_create(name=specialty_name)
                        new_specialties.append(specialty_obj)

                # Replace old with new
                user.specialties.set(new_specialties)

                # Delete specialties no longer used by any user
                Specialty.objects.annotate(user_count=models.Count('user')).filter(user_count=0).delete()


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
                        'specialties': [s.name for s in user.specialties.all()]
                    }
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'message': f"Profile update failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)


class GetProfileView(APIView):
    permission_classes = [IsAuthenticated, IsTasksmith]

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


class ChangePasswordView(APIView):
    """
    Allow authenticated users to change their password securely.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data

        current_password = data.get("current_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not current_password or not new_password or not confirm_password:
            return Response({
                'success': False,
                'message': 'All fields (current_password, new_password, confirm_password) are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({
                'success': False,
                'message': 'Current password is incorrect.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if new_password != confirm_password:
            return Response({
                'success': False,
                'message': 'New password and confirmation do not match.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(new_password):
            return Response({
                'success': False,
                'message': 'New password cannot be the same as the current password.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({
            'success': True,
            'message': 'Your password has been updated successfully.'
        }, status=status.HTTP_200_OK)

class DashboardView(APIView):
    """
    Return task statistics for the authenticated user, excluding deleted tasks.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_tasks = TasksDetail.objects.filter(user=user, deleted_at__isnull=True)

        # Task counts by status
        total_tasks = user_tasks.count()
        pending_tasks = user_tasks.filter(task_status='pending').count()
        review_tasks = user_tasks.filter(task_status='review').count()
        completed_tasks = user_tasks.filter(task_status='completed').count()

        return Response({
            'success': True,
            'message': 'Dashboard stats fetched successfully.',
            'data': {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'review_tasks': review_tasks,
                'completed_tasks': completed_tasks
            }
        }, status=status.HTTP_200_OK)

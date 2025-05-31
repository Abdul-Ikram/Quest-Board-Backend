from rest_framework import serializers
from .models import TasksDetail

class TaskUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasksDetail
        fields = ['task_title', 'task_description', 'task_url']

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        task_url = attrs.get('task_url')

        if user and TasksDetail.objects.filter(
            user=user,
            task_url=task_url,
            deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError({
                'task_url': 'You have already uploaded this task with this URL.'
            })

        return attrs

class GetTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasksDetail
        fields = [
            'id', 'task_title', 'task_description', 'task_url', 'demand_side',
        ]

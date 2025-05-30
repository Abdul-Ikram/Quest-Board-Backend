from rest_framework import serializers
from .models import TasksDetail

class TaskUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasksDetail

        fields = ['task_title', 'task_description', 'task_benefit', 'submit_sample', 'task_url']

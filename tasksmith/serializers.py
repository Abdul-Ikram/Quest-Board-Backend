from rest_framework import serializers
from .models import TasksDetail, Requirements, Tags
from authentication.models import User

class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirements
        fields = ['name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['name']


class TaskUploadSerializer(serializers.ModelSerializer):
    task_requirements = RequirementSerializer(many=True, required=False)
    task_tags = TagSerializer(many=True, required=False)

    class Meta:
        model = TasksDetail
        fields = [
            'task_assignment_type',
            'task_title',
            'task_reward_per_completion',
            'task_category',
            'task_description',
            'task_maximum_completions',
            'task_requirements',
            'task_tags',
            'task_status',
        ]

    def validate(self, attrs):
        task_assignment_type = attrs.get('task_assignment_type')
        task_maximum_completions = attrs.get('task_maximum_completions')

        if task_assignment_type == 'multiple' and not task_maximum_completions:
            raise serializers.ValidationError({
                'task_maximum_completions': 'This field is required when task_assignment_type is "multiple".'
            })
        return attrs

    def create(self, validated_data):
        req_data = validated_data.pop('task_requirements', [])
        tag_data = validated_data.pop('task_tags', [])
        task = TasksDetail.objects.create(**validated_data)

        for req in req_data:
            obj, _ = Requirements.objects.get_or_create(name=req['name'])
            task.task_requirements.add(obj)

        for tag in tag_data:
            obj, _ = Tags.objects.get_or_create(name=tag['name'])
            task.task_tags.add(obj)

        return task



class GetTasksSerializer(serializers.ModelSerializer):
    task_requirements = RequirementSerializer(many=True, read_only=True)
    task_tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = TasksDetail
        fields = [
            'id',
            'task_title',
            'task_description',
            'task_assignment_type',
            'task_reward_per_completion',
            'task_category',
            'task_requirements',
            'task_tags',
            'task_maximum_completions',
            'task_status',
            'created_at',
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'bio', 'company',
            'location', 'phone_number', 'website', 'total_tasks', 'tasks_completed', 'wallet_balance',
        ]

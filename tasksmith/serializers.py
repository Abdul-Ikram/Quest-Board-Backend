from rest_framework import serializers
from .models import TasksDetail, Requirements, Tags

class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirements
        fields = ['name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['name']


class TaskUploadSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = TasksDetail
        fields = [
            'task_assignment_type',
            'task_title',
            'reward_per_completion',
            'task_category',
            'task_description',
            'maximum_completions',
            'requirements',
            'tags',
        ]

    def validate(self, attrs):
        task_assignment_type = attrs.get('task_assignment_type')
        maximum_completions = attrs.get('maximum_completions')

        if task_assignment_type == 'multiple' and not maximum_completions:
            raise serializers.ValidationError({
                'maximum_completions': 'This field is required when task_assignment_type is "multiple".'
            })
        return attrs

    def create(self, validated_data):
        req_data = validated_data.pop('requirements', [])
        tag_data = validated_data.pop('tags', [])
        task = TasksDetail.objects.create(**validated_data)

        for req in req_data:
            obj, _ = Requirements.objects.get_or_create(name=req['name'])
            task.requirements.add(obj)

        for tag in tag_data:
            obj, _ = Tags.objects.get_or_create(name=tag['name'])
            task.tags.add(obj)

        return task



class GetTasksSerializer(serializers.ModelSerializer):
    requirements = RequirementSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = TasksDetail
        fields = [
            'id',
            'task_title',
            'task_description',
            'task_assignment_type',
            'reward_per_completion',
            'task_category',
            'requirements',
            'tags',
            'maximum_completions',
            'created_at',
            'updated_at',
        ]

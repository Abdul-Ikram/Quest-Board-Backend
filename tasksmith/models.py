from django.db import models
from authentication.models import User

# Create your models here.

TASK_STATUSES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('review', 'Review'),
    ('completed', 'Completed'),
    ('in_progress', 'InProgress'),
    ('submitted', 'Submitted'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
]

class Tags(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'task_tags'

    def __str__(self):
        return self.name


class Requirements(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'task_requirements'

    def __str__(self):
        return self.name

class TasksDetail(models.Model):
    # demand_side = models.CharField(max_length=50, null=False, blank=False)
    # task_benefit = models.IntegerField(default=0, null=False, blank=False)
    # submit_sample = models.URLField(max_length=500, null=True, blank=True)
    # task_url = models.URLField(max_length=500, null=False, blank=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_assignment_type = models.CharField(max_length=50, null=False, blank=False)
    task_title = models.CharField(max_length=50, null=False, blank=False, default='other')
    task_reward_per_completion = models.IntegerField(null=False, blank=False)
    task_category = models.CharField(max_length=100, null=False, blank=False, default='other')
    task_description = models.CharField(max_length=1000, null=False, blank=False, default='other')
    task_requirements = models.ManyToManyField(Requirements, blank=True)
    task_tags = models.ManyToManyField(Tags, blank=True)
    task_maximum_completions = models.IntegerField(null=True, blank=True, default=1)
    task_status = models.CharField(max_length=100, null=False, blank=False, choices=TASK_STATUSES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tasks_detail'

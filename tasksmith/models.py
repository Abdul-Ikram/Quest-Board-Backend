from django.db import models
from authentication.models import User

# Create your models here.

class TasksDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    demand_side = models.CharField(max_length=50, null=False, blank=False)
    task_title = models.CharField(max_length=50, null=False, blank=False, default='youtube')
    task_description = models.CharField(max_length=255, null=False, blank=False, default='youtube')
    task_benefit = models.IntegerField(default=0, null=False, blank=False)
    submit_sample = models.URLField(max_length=500, null=True, blank=True)
    task_url = models.URLField(max_length=500, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'tasks_detail'

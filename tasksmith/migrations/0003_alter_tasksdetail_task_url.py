# Generated by Django 5.1.4 on 2025-05-30 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasksmith', '0002_alter_tasksdetail_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasksdetail',
            name='task_url',
            field=models.URLField(max_length=500, unique=True),
        ),
    ]

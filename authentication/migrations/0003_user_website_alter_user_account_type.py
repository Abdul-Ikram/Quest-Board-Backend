# Generated by Django 5.1.4 on 2025-07-01 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_rename_role_user_account_type_user_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='website',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='account_type',
            field=models.CharField(choices=[('tasksmith', 'Tasksmith'), ('user', 'User')], default='user', max_length=50),
        ),
    ]

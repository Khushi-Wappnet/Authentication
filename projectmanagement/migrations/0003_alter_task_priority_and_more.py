# Generated by Django 4.2.20 on 2025-04-08 07:48

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projectmanagement', '0002_task_dependency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], max_length=6),
        ),
        migrations.AlterUniqueTogether(
            name='projectteammember',
            unique_together={('project', 'user')},
        ),
    ]

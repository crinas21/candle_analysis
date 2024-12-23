# Generated by Django 5.1.3 on 2024-12-20 03:58

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='days',
            field=models.PositiveIntegerField(default=30),
        ),
        migrations.AddField(
            model_name='history',
            name='search_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='history',
            name='symbol',
            field=models.CharField(default='UNKNOWN', max_length=10),
        ),
        migrations.AddField(
            model_name='history',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='search_history', to=settings.AUTH_USER_MODEL),
        ),
    ]

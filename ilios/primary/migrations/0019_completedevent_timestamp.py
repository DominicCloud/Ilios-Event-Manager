# Generated by Django 5.0.4 on 2024-05-02 07:50

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primary', '0018_alter_profiledetail_profile_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='completedevent',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

# Generated by Django 4.2.6 on 2024-03-28 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primary', '0003_rename_events_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.CharField(max_length=30),
        ),
    ]

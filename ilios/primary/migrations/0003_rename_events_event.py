# Generated by Django 4.2.6 on 2024-03-28 07:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('primary', '0002_events'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Events',
            new_name='Event',
        ),
    ]

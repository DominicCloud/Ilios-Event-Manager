# Generated by Django 4.2.6 on 2024-03-28 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('primary', '0004_alter_event_event_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='LikedEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='primary.event')),
                ('user_profile', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='primary.profile')),
            ],
        ),
    ]

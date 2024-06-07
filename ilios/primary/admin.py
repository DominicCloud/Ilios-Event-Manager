from django.contrib import admin
from .models import Profile, Event, LikedEvent, ProfileDetail, RegisteredEvent, CompletedEvent
# Register your models here.

admin.site.register(Profile)
admin.site.register(Event)
admin.site.register(LikedEvent)
admin.site.register(ProfileDetail)
admin.site.register(RegisteredEvent)
admin.site.register(CompletedEvent)

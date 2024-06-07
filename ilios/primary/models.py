from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Super User info
'''
fin : 123
dom : 321 ...missing
'''

# Regular user info
'''
*cal : 1
nig : mikey
al : jake ...incorrect password
*jj : qwe
norva : nigel
quin : 456

'''

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    college = models.CharField(max_length=200)
    isHost = models.BooleanField(default=False, null=True)

    def __str__(self):
        return str(self.user)
    
class Event(models.Model):
    creator = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    bgimg = models.ImageField(upload_to='images/events/', null=True, blank=True)
    event_type = models.CharField(max_length=30)
    description = models.TextField()
    event_date = models.DateTimeField()
    event_duration = models.IntegerField()
    tags = models.JSONField()
    contact_info = models.JSONField()
    required_details = models.JSONField(null=True, blank=True)
    expiry_timer = models.IntegerField(null=True, blank=True, default=100)

    def __str__(self):
        return str(self.title+' | '+self.event_type)
    
class LikedEvent(models.Model):
    user_profile = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_profile.user.username+' liked '+self.event.title)
    

class ProfileDetail(models.Model):
    user_profile = models.OneToOneField(Profile, null=True, on_delete=models.CASCADE)
    profile_img = models.ImageField(upload_to='images/profiles/', null=True, blank=True)
    college_class = models.CharField(max_length=10, null=True, blank=True)
    branch = models.CharField(max_length=10, null=True, blank=True)
    roll_no = models.IntegerField(null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    interests = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.user_profile)+"'s details"

class RegisteredEvent(models.Model):
    user_profile = models.ForeignKey(ProfileDetail, null=True, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    additional_details = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    qr_string = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.user_profile.user_profile)+' registered for '+str(self.event.title)
    
class CompletedEvent(models.Model):
    event_data = models.OneToOneField(RegisteredEvent, null=True, on_delete=models.CASCADE)
    rating = models.FloatField(null=True, blank=True, default=0, 
                               validators=[
            MinValueValidator(limit_value=0.1),  # Set your minimum value here
            MaxValueValidator(limit_value=5.0)  # Set your maximum value here
        ])
    review = models.TextField(null=True, blank=True,)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_data.user_profile.user_profile} gave {self.event_data.event} a rating of {self.rating}"
    




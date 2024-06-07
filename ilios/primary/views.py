from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count
from primary.models import Profile, Event, LikedEvent, ProfileDetail, RegisteredEvent, CompletedEvent
from datetime import datetime
import pytz
import re
import hashlib, hmac, qrcode, base64
from io import BytesIO
from django.core.mail import send_mail
# from primary.ml import *

# Helper Functions
def strong_password_checker(password):
    # Check minimum length
    if len(password) < 8:
        return False
    # Check for at least one uppercase character
    if not any(char.isupper() for char in password):
        return False
    # Check for at least one special character
    if not re.search(r"[!@#$%^&*()-+=]", password):
        return False
    # If all criteria are met, return True
    return True

def group_elements(lst):
    grouped = []
    group = []
    for i, item in enumerate(lst, 1):
        group.append(item)
        if i % 3 == 0:
            grouped.append(group)
            group = []
    if group:
        grouped.append(group)
    return grouped

def clean_phone_number(phone_number):
    # Remove unwanted characters from phone number
    cleaned_number = re.sub(r'[-. ()+]', '', phone_number)
    return cleaned_number

def extract_contacts(contact_info_arr):
    phone_numbers = []
    emails = []

    for item in contact_info_arr:
        # Extract phone numbers
        phone_matches = re.findall(r'\+?[0-9]+[-. ()]*[0-9]+[-. ()]*[0-9]+', item)
        for match in phone_matches:
            cleaned_number = clean_phone_number(match)
            if cleaned_number == 10:
                phone_numbers.append(cleaned_number)

        # Extract email addresses
        email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', item)
        emails.extend(email_matches)

    return phone_numbers, emails

def generate_dynamic_string(attribute, secret_key):
    message = f"{attribute}"
    dynamic_string = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return dynamic_string

def generate_qr_code(dynamic_string):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(dynamic_string)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")

def update_expiry_timer():
    timezone = pytz.timezone('Asia/Kolkata')
    current = timezone.localize(datetime.now())
    events = Event.objects.all()
    for event in events:
        difference = event.event_date - current
        hours_left = difference.total_seconds() / 3600  # Convert difference to hours
        event.expiry_timer = 0 if hours_left <= 0 else int(hours_left)
        event.save()

def created_success_mail(event, creator_mail):
    mail_subject = f"Event {event.title} is now live!"
    message = f'''{event.title} has been successfully posted for the world to see!\n
    The details of the events are:\n
    Date:{event.event_date}\n
    Event Duration: {event.event_duration}\n
    Additional Details Requested: {event.required_details}\n
    Thank You for choosing ilios.
    '''
    send_mail(
        mail_subject,
        message,
        "ilios.incorporated@gmail.com",
        [creator_mail]
    )
    print(f"Mail send to creator with mail id {creator_mail}!")

def register_success_mail(profile, event):
    mail_subject = f"Successfully registered for Event {event.title}!"
    message = f'''{event.title} is happening on {event.event_date}, and thanks to us, you'll be there for it too!\n
    The details of the events are:\n
    Date:{event.event_date}\n
    Event Duration: {event.event_duration}\n
    Additional Details Requested: {event.required_details}\n\n
    Hop back on and keep registering, because the events never stop!
    '''
    send_mail(
        mail_subject,
        message,
        "ilios@gmail.com",
        [profile.user_profile.user.email]
    )
    print(f"Mail send to creator with mail id {profile.user_profile.user.email}!")
# Create your views here.

def home(request):

    if request.user.is_superuser:
        messages.info(request, 'Superuser Detected ... Redirecting to Admin Panel')
        return redirect('/admin/')
    if request.user.is_authenticated:
        user_profile = Profile.objects.filter(user=request.user)[0]
        return render(request, 'home.html', {'profile':user_profile})
    else:
        return redirect('/login')


def about(request):
    p = Profile.objects.get(user=request.user)
    return render(request, 'about.html', {'profile':p})


def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        fname, lname = fullname.split()
        username = request.POST.get('username')
        email = request.POST.get('email')
        pwd1 = request.POST.get('pwd1')
        pwd2 = request.POST.get('pwd2')
        phone = clean_phone_number(request.POST.get('phone'))
        college = request.POST.get('college')
        isHost = bool(request.POST.get('role'))
        print(fname, username, lname, email, pwd1, pwd2, phone, college, isHost)
    
        if User.objects.filter(username=username).exists():
            messages.info(request, f'Username {username} already exists :(')
            return redirect('/register')
        elif pwd1!=pwd2:
            messages.info(request, 'Passwords do not match!')
            return redirect('/register')
        # elif not strong_password_checker(pwd1):
        #     messages.info(request, 'Password should be minimum length 8, contain at least one uppercase and special case character!')
        #     return redirect('/register')
        else:
            user = User.objects.create_user(username=username, first_name=fname, last_name=lname, password=pwd1, email=email)
            user.save()
            prof = Profile.objects.create(user=user, phone=phone, college=college, isHost=isHost)
            prof.save()

            user = authenticate(username=username, password=pwd1)
            login(request, user)
            print("Logged in")
            
            return redirect('/')
 
    return render(request, 'register.html')


def loginUser(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/login')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pwd1')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            print('Incorrect username or password')
            messages.info(request, 'Incorrect username or password')
            return render(request, 'login.html')
    # No backend authenticated the credentials
    return render(request, 'login.html')

def logoutUser(request):
    if request.user.is_authenticated:
        print(f"Logging out authenticated user {request.user}")
        logout(request)
        return redirect('/')        
    else:
        print('not logged in, redirecting to login page now')
        return redirect('/login')


def events(request):
    u_profile = Profile.objects.filter(user=request.user)[0]
    update_expiry_timer()
    #events_collection = Event.objects.filter(date_of_creation__gte=current) # filter out expired events
    events_collection = Event.objects.all().order_by('-expiry_timer') # get all events
    context = {'events':events_collection, 'profile':u_profile}

    return render(request, 'events.html', context)

def auto_register(request, event_id):
    print("Reached here")
    profile = Profile.objects.get(user=request.user)

    if not ProfileDetail.objects.filter(user_profile=profile).exists():
        messages.info(request, f'Please complete filling of all details')
        return redirect('profile')
    
    profile_details = ProfileDetail.objects.get(user_profile=profile)
    event = Event.objects.get(id=event_id)
    if event.required_details:
            return redirect(f'/event-registration/{event_id}')
    else:
        reg_event = RegisteredEvent.objects.filter(user_profile=profile_details, event=event)
        if reg_event.exists():
            messages.info(request, f'You have already registered for {event.title}')
            return redirect('/events')
        else:
            temp = str(profile_details.id)+str(profile)+str(event.id)+str(event.title)
            secret_key = "d8f2a7b4e6c9a0f1d3b5e8c7a2f4e6c8"
            dynamic_string = generate_dynamic_string(temp, secret_key)
            
            registered_event = RegisteredEvent.objects.create(user_profile=profile_details, event=event, qr_string=dynamic_string)
            registered_event.save()
            messages.info(request, 'Event Successfully Registered!')
            return redirect('/events')

    

def event_registration_redirect(request, event_id):
    profile = ProfileDetail.objects.get(user_profile=Profile.objects.get(user=request.user))
    print(profile)
    event = Event.objects.get(id=event_id)
    print(event)
    if request.method == "POST":
        if RegisteredEvent.objects.filter(user_profile=profile, event=event):
            reg_event = RegisteredEvent.objects.get(user_profile=profile, event=event).timestamp
            messages.info(request, f'Already Registered for this Event on {reg_event}')
            return redirect('/events')
        else:
            add_details = request.POST.get('details')
            if add_details:
                add_details = add_details.strip().split(",")

            temp = str(profile.id)+str(profile.user_profile)+str(event.id)+str(event.title)
            secret_key = "d8f2a7b4e6c9a0f1d3b5e8c7a2f4e6c8"
            dynamic_string = generate_dynamic_string(temp, secret_key)

            registered_event = RegisteredEvent.objects.create(user_profile=profile, event=event, qr_string=dynamic_string)
            registered_event.save()

            if add_details:
                registered_event.additional_details = add_details
                registered_event.save()

            register_success_mail(profile=profile, event=event)

                
            messages.info(request, 'Event Successfully Registered!')

    return redirect('/events')

def liked(request, event_id):
    user_profile = Profile.objects.filter(user=request.user)[0]
    requested_event = Event.objects.filter(id=event_id)[0]

    like_exists = LikedEvent.objects.filter(user_profile=user_profile, event=requested_event).exists()

    if like_exists:
        messages.info(request, 'You have already liked this event')
    else:
        new_tuple = LikedEvent.objects.create(user_profile=user_profile, event=requested_event)
        new_tuple.save()
        messages.info(request, f'Event {requested_event.title} added to liked Events')
        print(f'Event {requested_event.title} added to liked Events')
    return redirect('/events')


def create(request):
    user_profile = Profile.objects.filter(user=request.user)[0]
    if request.method == "POST":
        creator = user_profile
        title = request.POST.get('title')
        event_type = request.POST.get('event_type')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        event_duration = request.POST.get('event_duration')
        tags = request.POST.get('tags').strip().split(",")
        contact_info = extract_contacts(request.POST.get('contact_info').strip().split(","))
        required_details = request.POST.get('required_details').strip().split(",")
        bgimg = request.FILES.get('bgimg')

        if Event.objects.filter(title=title).exists():
            messages.info(request, 'An event with this title already exists! Kindly pick a different title.')
            return redirect('/create')
        
        event  = Event.objects.create(creator=creator,title=title,event_type=event_type,description=description,event_date=event_date,event_duration=event_duration,tags=tags,contact_info=contact_info)
        event.save()

        new_event_created = Event.objects.get(title=title)

        creator_mail = user_profile.user.email

        created_success_mail(event=new_event_created, creator_mail=creator_mail)

        if len(required_details[0]):
            new_event_created.required_details = required_details
            new_event_created.save()
        if bgimg:
            new_event_created.bgimg = bgimg
            new_event_created.save()

        messages.info(request, 'Event Created!')
        return redirect('/events')
        
    return render(request, 'create.html', {"profile":user_profile})


def dash_view(request):
    return render(request, 'dash.html')

def dash_liked(request):
    liked_data = []
    reg_data = []
    profile = Profile.objects.filter(user=request.user, isHost=True)[0]
    events = Event.objects.filter(creator=profile)
    for event in events:
        if LikedEvent.objects.filter(event=event):
            like_tuple = LikedEvent.objects.filter(event=event)
            liked_data.append(like_tuple[::-1])

    print(liked_data)
    return render(request, 'dash_liked.html', {'liked_data':liked_data, 'events':events, 'reg_data':reg_data})


def dash_reg(request):
    liked_data = []
    reg_data = []
    profile = Profile.objects.filter(user=request.user, isHost=True)[0]
    events = Event.objects.filter(creator=profile)
    for event in events:
        if RegisteredEvent.objects.filter(event=event):
            reg_tuple = RegisteredEvent.objects.filter(event=event)
            reg_data.append(reg_tuple[::-1])
        else:
            print(f"reached here for event {event}")
            reg_data.append([{'user_profile':'----', 'event':'No liked events', 'timestamp':'--|--|--'}])
            continue

    return render(request, 'dash_reg.html', {'liked_data':liked_data, 'events':events, 'reg_data':reg_data})

def dash_analytics(request):
    update_expiry_timer()
    
    registrations = 0
    likes = 0
    ratings = 0
    total = 0
    timezone = pytz.timezone('Asia/Kolkata')
    current = timezone.localize(datetime.now())
    
    profile = Profile.objects.get(user=request.user)
    events = Event.objects.filter(creator=profile)

    for event in events:
        registered_events = RegisteredEvent.objects.filter(event=event)
        liked_events = LikedEvent.objects.filter(event=event)
        registrations += len(registered_events)
        for e in liked_events:
            difference = current - e.timestamp
            hours_left = difference.total_seconds() / 3600
            if hours_left <= 24:
                likes += 1
        for e in registered_events:
            completed_events = CompletedEvent.objects.filter(event_data=e)
            for reg_event in completed_events:
                ratings += reg_event.rating
                total += 1

    if total==0:
        avg_ratings = 0
    else:
        avg_ratings = round(ratings/total, 2)

    return render(request, 'analytics.html', {'registrations': registrations, 'avg_ratings':avg_ratings, 'likes':likes})

def profile(request):
    user_profile = Profile.objects.filter(user=request.user)[0]

    if ProfileDetail.objects.filter(user_profile=user_profile):
        details = ProfileDetail.objects.filter(user_profile=user_profile)[0]
        if RegisteredEvent.objects.filter(user_profile=details):
            reg_events = RegisteredEvent.objects.filter(user_profile=details)
        else:
            reg_events = []            
    else:
        details = []
        reg_events = []
    view_mode = False

    if request.method == 'POST':
        college_class = request.POST.get('col_class')
        roll_no = request.POST.get('roll_number')
        branch = request.POST.get('branch')
        pid = request.POST.get('pid_uid')
        interests = request.POST.get('interests')
        profile_img = request.FILES.get('profile_img')
        interests_arr = re.findall(r'\w+', interests)
        print(f"New:{profile_img}")


        user_profile = Profile.objects.filter(user=request.user)[0]

        if ProfileDetail.objects.filter(user_profile=user_profile).exists():
            prof_details = ProfileDetail.objects.get(user_profile=user_profile)
            print(f"Before:{prof_details.profile_img}")
            if profile_img:
                prof_details.profile_img = profile_img
                prof_details.save()
                print(f"After:{prof_details.profile_img}")
            ProfileDetail.objects.filter(user_profile=user_profile).update(college_class=college_class, branch=branch, roll_no=roll_no, pid=pid, interests=interests_arr)
            messages.info(request, "Details Updated Successfully")
        else:
            new_details = ProfileDetail.objects.create(user_profile=user_profile, college_class=college_class, branch=branch, roll_no=roll_no, pid=pid, interests=interests_arr, profile_img=profile_img)
            new_details.save()
            messages.info(request, "Details Added Successfully")
        details = ProfileDetail.objects.filter(user_profile=user_profile)[0]

    return render(request, 'profile.html', {'profile':user_profile, 'view_mode':view_mode, 'details':details, 'reg_events':reg_events})


def view_profile(request, user):    
    user_obj = User.objects.get(username=user)
    user_profile = Profile.objects.get(user=user_obj)
    details = []
    if ProfileDetail.objects.filter(user_profile=user_profile):
        details = ProfileDetail.objects.get(user_profile=user_profile)
    view_mode = True
    return render(request, 'profile.html', {'profile':user_profile, 'view_mode':view_mode, 'details':details})


def edit_details(request, user):    
    user_obj = User.objects.get(username=user)
    user_profile = Profile.objects.get(user=user_obj)
    details = ''
    if ProfileDetail.objects.filter(user_profile=user_profile).exists():
        details = ProfileDetail.objects.get(user_profile=user_profile)

    view_mode = False
    return render(request, 'edit_profile.html', {'profile':user_profile, 'view_mode':view_mode, 'details':details})


def bookmarks(request):
    update_expiry_timer()
    profile = Profile.objects.get(user=request.user)
    events_list = []
    user_profile = Profile.objects.get(user=request.user)
    liked_events_list = LikedEvent.objects.filter(user_profile=user_profile).values('event') # Returns a dictionary with key as 'event' and value as the event id
    events_list = [Event.objects.filter(id=i['event'])[0] for i in liked_events_list]
    return render(request, 'bookmarks.html', {'liked_events':events_list, 'profile':profile})


def event_register(request, event_id):
    profile = ''
    can_review = False
    event = Event.objects.get(id=event_id)
    p = Profile.objects.get(user=request.user)
    reviews = []
    if RegisteredEvent.objects.filter(event=event).exists():
        for e in RegisteredEvent.objects.filter(event=event):
            print(f"{e.user_profile.user_profile} registered")
            if CompletedEvent.objects.filter(event_data=e).exists():
                reviews.append(CompletedEvent.objects.filter(event_data=e))
    
    if ProfileDetail.objects.filter(user_profile=p).exists():
        profile = ProfileDetail.objects.get(user_profile=p)

    if RegisteredEvent.objects.filter(user_profile=profile, event=event).exists():
        can_review = True
    return render(request, 'event_register.html', {'event':event, 'profile':profile, 'p':p, 'all_reviews':reviews, 'reviewable':can_review})

def ticket(request, registered_event_id):
    ticket = RegisteredEvent.objects.filter(event=Event.objects.filter(id=registered_event_id)[0])[0]
    dynamic_string = ticket.qr_string
    event = ticket.event

    qr_code = generate_qr_code(dynamic_string)
    qr_code_base64 = base64.b64encode(qr_code.content).decode('utf-8')
    # qr_string = registered_event.qr_string
    
    return render(request, 'event_ticket.html', {'event':event, 'ticket':ticket, 'dynamic_string':dynamic_string, 'qr_code_content':qr_code_base64})


def ratings(request, registered_event_id):
    event = Event.objects.get(id=registered_event_id)
    
    p = Profile.objects.get(user=request.user)
    if not ProfileDetail.objects.filter(user_profile=p).exists:
        messages.info(request, 'You have not created a profile yet')
        return redirect('/profile')

    prof = ProfileDetail.objects.get(user_profile=p)

    if not RegisteredEvent.objects.filter(user_profile=prof, event=event).exists():
        messages.info(request, 'You cannot review an event you did not register for!')
        return redirect('/bookmarks')
    
    ticket = RegisteredEvent.objects.filter(user_profile=prof, event=event)[0]

    if request.method == "POST":
        event_data = ticket
        review = request.POST.get('reviews')
        rating = request.POST.get('ratings')
        print(event_data, review, rating)

        if CompletedEvent.objects.filter(event_data=event_data).exists():
            messages.info(request, 'You have already submitted your review for this Event')
            return redirect('/profile')
        else:
            new_review = CompletedEvent.objects.create(event_data=event_data, rating=rating, review=review)
            new_review.save()
            messages.info(request, 'Review successfully submitted!')
            return redirect('/profile')
    return render(request, 'event_ratings.html', {'ticket':ticket, 'event':ticket.event})


def events_two(request):
    profile = Profile.objects.get(user=request.user)
    details = ProfileDetail.objects.get(user_profile=profile)
    # finalFunc()
    return render(request, 'events-2.html', {'profile':profile, 'details':details})


def old_about(request, url): #Optional : allows redirecting of old URLs
    return redirect('/about')

def custom_404(request, url_path):
    return render(request, '404.html', status=404)

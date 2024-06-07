# URLs for our app primary

from django.urls import path
from primary import views
from django.conf.urls import handler404

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('register', views.register, name='register'),
    path('login', views.loginUser, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('events', views.events, name='events'),
    path('events/<int:event_id>', views.event_registration_redirect, name='event-reg-redirect'),
    path('events/liked/<int:event_id>', views.liked, name='liked-events'),
    path('create', views.create, name='create'),
    path('dashboard', views.dash_view, name='dashboard'),
    path('dashboard/liked', views.dash_liked, name='dashboard-liked-events'),
    path('dashboard/registered', views.dash_reg, name='dashboard-registrations'),
    path('dashboard/analytics', views.dash_analytics, name='dashboard-analytics'),
    path('bookmarks', views.bookmarks, name='bookmarks'),
    path('events-2', views.events_two, name='event-2'),
    path('profile', views.profile, name='profile'),
    path('event-registration/<int:event_id>', views.event_register, name='event-registration'),
    path('auto-register-redirect/<int:event_id>', views.auto_register, name="auto-register"),
    path('profile/<user>', views.view_profile, name='profile-view'),
    path('profile/edit/<user>', views.edit_details, name='edit-details'),
    path('about<url>', views.old_about, name='about-redirect'),
    path('event-ticket/<registered_event_id>', views.ticket, name="event-ticket"),
    path('event-ratings/<registered_event_id>', views.ratings, name="event-ratings"),

    # path('<path:url_path>', views.custom_404, name='custom_404'), # 404 url handler
]

handler404 = views.custom_404 # built-in function that prevents error from raising
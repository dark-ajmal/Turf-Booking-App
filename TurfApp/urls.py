from django.urls import path
from . import views

# This is the app's URL configuration.
# The name 'owner_view' is used for the main dashboard URL.
urlpatterns = [
    # Authentication & General Views
    path('login/', views.login_view, name='login_view'),
    path('signup/', views.signup_view, name='signup_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('', views.landing_view, name='landing_view'),

    # Player Views
    path('home/', views.home_view, name='home_view'),
    path('turfs/', views.home_turf_view, name='home_turf_view'),
    path('booking/<int:turf_id>/', views.booking_view_player, name='booking_page'),
    path('receipt/<int:booking_id>/', views.booking_receipt_view, name='booking_receipt'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),

    # Owner Views
    path('ownerdashboard/', views.owner_dashboard_view, name='owner_view'),
    path('turf/add/', views.turf_view, name='turf_add'),
    path('turf/<int:turf_id>/edit/', views.edit_turf, name='edit_turf'),
    path('turf/<int:turf_id>/bookings/', views.view_bookings, name='view_bookings'),
    path('owner/booking/<int:booking_id>/', views.owner_booking_detail_view, name='owner_booking_detail'),
    path('turf/<int:turf_id>/slots/', views.manage_slots, name='manage_slots'),

    # Placeholder/Static Views
    path('cricket/', views.cricket_view, name='cricket_view'),
    path('football/', views.football_view, name='football_view'),
    path('badminton/', views.badminton_view, name='badminton_view'),
]


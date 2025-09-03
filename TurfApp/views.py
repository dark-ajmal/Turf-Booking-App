from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import datetime, timedelta, date, time
from .models import TurfUser, TurfVenue, Booking, Rating, Transaction
from .forms import UpdateProfileForm, PasswordChangeForm, TurfVenueForm
from decimal import Decimal
from django.db.models import Q, Sum, Count, Avg, Min, Max
from django.db.models.functions import TruncMonth, TruncDay
from django.core.paginator import Paginator
from django.urls import reverse
import calendar

# -----------------------------------------------------------------------------
# Helper Functions for Role Checks
# -----------------------------------------------------------------------------

def is_player(user):
    """Checks if the user is an authenticated player."""
    return user.is_authenticated and user.role == 'player'

def is_owner(user):
    """Checks if the user is an authenticated owner."""
    return user.is_authenticated and user.role == 'owner'

# -----------------------------------------------------------------------------
# Authentication & General Views
# -----------------------------------------------------------------------------

def login_view(request):
    """Handles user login."""
    if request.user.is_authenticated:
        return redirect('home_view' if request.user.role == 'player' else 'owner_view')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect('home_view' if user.role == 'player' else 'owner_view')
        else:
            messages.error(request, "Invalid email or password.")
            
    return render(request, 'login.html')

def signup_view(request):
    """Handles new user registration."""
    if request.user.is_authenticated:
        return redirect('home_view' if request.user.role == 'player' else 'owner_view')

    if request.method == 'POST':
        name = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if TurfUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "signup.html")

        user = TurfUser.objects.create_user(
            username=email, name=name, password=password, email=email,
            phone=request.POST.get('phone'), role=request.POST.get('user_type', 'player')
        )
        login(request, user)
        messages.success(request, "Signup successful! Welcome.")
        return redirect('home_view' if user.role == 'player' else 'owner_view')
            
    return render(request, 'signup.html')

@login_required
def logout_view(request):
    """Logs the current user out."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing_view')

def landing_view(request):
    """Displays the main landing page."""
    return render(request, 'landing.html')

# -----------------------------------------------------------------------------
# Player Views
# -----------------------------------------------------------------------------

@login_required
@user_passes_test(is_player)
def home_view(request):
    """Displays all available turfs for players."""
    turfs = TurfVenue.objects.all()
    return render(request, 'home.html', {'turfs': turfs})

@login_required
@user_passes_test(is_player)
def home_turf_view(request):
    """Displays a filterable list of turfs."""
    turfs = TurfVenue.objects.all()
    return render(request, 'home_turfs.html', {'turfs': turfs})

@login_required
@user_passes_test(is_player)
def booking_view_player(request, turf_id):
    """Handles both displaying the booking page and creating a booking."""
    turf = get_object_or_404(TurfVenue, id=turf_id)

    if request.method == 'POST':
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        booking_date_str = request.POST.get('booking_date')
        players = request.POST.get('no_of_players', 1)

        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
        
        if booking_date < date.today():
            messages.error(request, "You cannot book a turf for a past date.")
            return redirect('booking_page', turf_id=turf.id)

        duration = (datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).total_seconds() / 3600
        total_price = Decimal(duration) * turf.price_per_hour

        booking = Booking.objects.create(
            turf=turf, player=request.user, date=booking_date,
            start_time=start_time, end_time=end_time,
            total_price=total_price, no_of_players=players
        )
        
        Transaction.objects.create(
            booking=booking,
            amount=total_price,
            status='Completed'
        )
        
        messages.success(request, "Booking created successfully!")
        return redirect('booking_receipt', booking_id=booking.id)

    else: # GET Request
        selected_date_str = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        
        bookings_on_date = Booking.objects.filter(
            Q(status='Confirmed') | Q(status='Blocked'),
            turf=turf, 
            date=selected_date
        )
        
        booked_slots = set()
        for booking in bookings_on_date:
            current_slot = datetime.combine(selected_date, booking.start_time)
            end_time_dt = datetime.combine(selected_date, booking.end_time)
            while current_slot < end_time_dt:
                booked_slots.add(current_slot.time())
                current_slot += timedelta(minutes=30)

        slots = []
        if turf.open_time and turf.close_time:
            current_time = datetime.combine(selected_date, turf.open_time)
            close_time = datetime.combine(selected_date, turf.close_time)
            
            while current_time < close_time:
                slot_start_time = current_time.time()
                end_of_slot = current_time + timedelta(minutes=30)
                
                is_past = selected_date == date.today() and slot_start_time < (timezone.now() - timedelta(minutes=10)).time()
                is_booked = slot_start_time in booked_slots

                slots.append({
                    'start_time': slot_start_time,
                    'end_time': end_of_slot.time(),
                    'is_available': not is_booked and not is_past,
                })
                current_time = end_of_slot

        context = {
            'turf': turf, 
            'slots': slots,
            'selected_date': selected_date.strftime('%Y-%m-%d'),
        }
        return render(request, 'booking_player.html', context)

@login_required
@user_passes_test(is_player)
def my_bookings_view(request):
    """Fetches and displays all bookings for the current player."""
    bookings = Booking.objects.filter(player=request.user).select_related('turf').order_by('-date', '-start_time')
    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required
@user_passes_test(is_player)
def cancel_booking_view(request, booking_id):
    """Allows a player to cancel their own booking."""
    booking = get_object_or_404(Booking, id=booking_id, player=request.user)
    
    booking_start_datetime = timezone.make_aware(datetime.combine(booking.date, booking.start_time))
    
    if booking_start_datetime < timezone.now() + timedelta(hours=2):
        messages.error(request, "Cancellation is not allowed within 2 hours of the start time.")
        return redirect('my_bookings')

    booking.status = 'Cancelled'
    booking.save()
    messages.success(request, f"Your booking for {booking.turf.name} has been cancelled.")
    return redirect('my_bookings')

# --- FIX: ADDED THE MISSING VIEW ---
@login_required
@user_passes_test(is_player)
def booking_receipt_view(request, booking_id):
    """Displays a receipt for a specific booking."""
    booking = get_object_or_404(Booking, id=booking_id, player=request.user)
    return render(request, 'booking_receipt.html', {'booking': booking})

# -----------------------------------------------------------------------------
# Turf Owner Views
# -----------------------------------------------------------------------------

@login_required
@user_passes_test(is_owner)
def owner_dashboard_view(request):
    """The main dashboard for a turf owner, with dynamic stats, bookings, and settings."""
    owner = request.user
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UpdateProfileForm(request.POST, request.FILES, instance=owner)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
            else:
                messages.error(request, 'Please correct the errors in your profile form.')
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=owner, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was changed successfully.')
            else:
                messages.error(request, 'Please correct the errors in your password form.')
        
        redirect_url = reverse('owner_view') + '#settings'
        return redirect(redirect_url)
    
    else: # GET Request
        profile_form = UpdateProfileForm(instance=owner)
        password_form = PasswordChangeForm(user=owner)
    
    turfs = TurfVenue.objects.filter(owner=owner)
    today = date.today()
    start_of_month = today.replace(day=1)
    
    bookings_this_month = Booking.objects.filter(
        turf__owner=owner, date__gte=start_of_month, status='Confirmed'
    )
    
    total_bookings_count = bookings_this_month.count()
    revenue_data = bookings_this_month.aggregate(total=Sum('total_price'))
    total_revenue = revenue_data['total'] or 0
    avg_rating_data = Rating.objects.filter(turf__owner=owner).aggregate(avg=Avg('score'))
    average_rating = avg_rating_data['avg'] or 0.0

    stats = {
        'total_bookings': total_bookings_count, 'total_revenue': total_revenue,
        'average_rating': round(average_rating, 2), 'occupancy_rate': 0, # Placeholder
    }

    all_owner_bookings = Booking.objects.filter(turf__owner=owner).select_related('player', 'turf')
    recent_bookings = all_owner_bookings.order_by('-booked_at')[:5]
    
    all_bookings_paginator = Paginator(all_owner_bookings.order_by('-date', '-start_time'), 10)
    all_bookings_page = all_bookings_paginator.get_page(request.GET.get('page'))
    
    transactions_paginator = Paginator(Transaction.objects.filter(booking__turf__owner=owner).order_by('-created_at'), 10)
    transactions_page = transactions_paginator.get_page(request.GET.get('page_trans'))

    # ... (Analytics logic) ...
    chart_data = {'labels': [], 'revenue': [], 'bookings': []} # Placeholder for now

    context = {
        'turfs': turfs, 'stats': stats, 'recent_bookings': recent_bookings,
        'all_bookings': all_bookings_page,
        'transactions': transactions_page,
        'profile_form': profile_form,
        'password_form': password_form,
        'chart_data': chart_data,
        'analytics_filters': { 'years': range(2023, today.year + 2) },
    }
    
    # Today's Schedule Timeline Logic
    schedule_turfs = turfs
    if schedule_turfs.exists():
        min_open = schedule_turfs.aggregate(min=Min('open_time'))['min'] or time(8, 0)
        max_close = schedule_turfs.aggregate(max=Max('close_time'))['max'] or time(22, 0)
        
        start_hour = min_open.hour
        end_hour = max_close.hour + (1 if max_close.minute > 0 else 0)
        total_hours = end_hour - start_hour

        time_slots = [time(hour=h) for h in range(start_hour, end_hour)]
            
        bookings_today = Booking.objects.filter(
            turf__in=schedule_turfs, date=today
        ).exclude(status='Cancelled').select_related('player')

        for booking in bookings_today:
            if total_hours > 0:
                start_offset_minutes = (booking.start_time.hour - start_hour) * 60 + booking.start_time.minute
                total_timeline_minutes = total_hours * 60
                booking.start_offset_percent = (start_offset_minutes / total_timeline_minutes) * 100
                duration_minutes = booking.duration_in_hours * 60
                booking.duration_percent = (duration_minutes / total_timeline_minutes) * 100
            else:
                booking.start_offset_percent = 0
                booking.duration_percent = 0
        
        context['schedule_data'] = {
            'turfs': schedule_turfs, 
            'time_slots': time_slots, 
            'bookings': bookings_today,
            'start_hour': start_hour,
        }
    
    return render(request, 'ownerboard.html', context)

# ... (rest of owner and placeholder views) ...

@login_required
@user_passes_test(is_owner)
def turf_view(request):
    """View for an owner to create a new turf using a model form."""
    if request.method == 'POST':
        form = TurfVenueForm(request.POST, request.FILES)
        if form.is_valid():
            turf = form.save(commit=False)
            turf.owner = request.user
            turf.save()
            form.save_m2m() 
            messages.success(request, "Turf registered successfully!")
            return redirect('owner_view')
    else:
        form = TurfVenueForm()
    return render(request, 'turfs.html', {'form': form})

@login_required
@user_passes_test(is_owner)
def edit_turf(request, turf_id):
    """View for an owner to edit one of their turfs using a model form."""
    turf = get_object_or_404(TurfVenue, id=turf_id, owner=request.user)
    if request.method == 'POST':
        form = TurfVenueForm(request.POST, request.FILES, instance=turf)
        if form.is_valid():
            form.save()
            messages.success(request, "Turf updated successfully!")
            return redirect('owner_view')
    else:
        form = TurfVenueForm(instance=turf)
    return render(request, 'edit_turfs.html', {'form': form, 'turf': turf})

@login_required
@user_passes_test(is_owner)
def view_bookings(request, turf_id):
    """Allows an owner to see all bookings for one of their turfs."""
    turf = get_object_or_404(TurfVenue, id=turf_id, owner=request.user)
    bookings = Booking.objects.filter(turf=turf).order_by('-date', '-start_time')
    return render(request, 'view_bookings.html', {'turf': turf, 'bookings': bookings})

@login_required
@user_passes_test(is_owner)
def owner_booking_detail_view(request, booking_id):
    """Allows an owner to see the full details of a single booking."""
    booking = get_object_or_404(Booking, id=booking_id, turf__owner=request.user)
    return render(request, 'view_booking_detail.html', {'booking': booking, 'turf': booking.turf})

@login_required
@user_passes_test(is_owner)
def manage_slots(request, turf_id):
    """Allows a turf owner to view, block, and unblock time slots."""
    turf = get_object_or_404(TurfVenue, id=turf_id, owner=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        slot_date_str = request.POST.get('slot_date')
        slot_date = datetime.strptime(slot_date_str, '%Y-%m-%d').date()

        if action == 'block':
            start_time_str = request.POST.get('start_time')
            end_time_str = request.POST.get('end_time')
            reason = request.POST.get('reason', 'Maintenance')

            Booking.objects.create(
                turf=turf, player=None, date=slot_date,
                start_time=datetime.strptime(start_time_str, '%H:%M:%S').time(),
                end_time=datetime.strptime(end_time_str, '%H:%M:%S').time(),
                status='Blocked', block_reason=reason
            )
            messages.success(request, f"Slot on {slot_date_str} blocked successfully.")
        
        elif action == 'unblock':
            booking_id = request.POST.get('booking_id')
            booking_to_unblock = get_object_or_404(Booking, id=booking_id, turf=turf, status='Blocked')
            booking_to_unblock.delete()
            messages.success(request, f"Slot on {slot_date_str} is now available.")
            
        return redirect(f"{request.path}?date={slot_date_str}")

    selected_date_str = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    
    bookings_on_date = Booking.objects.filter(turf=turf, date=selected_date)
    
    booked_slots = {}
    for booking in bookings_on_date:
        booked_slots[booking.start_time] = booking

    slots = []
    if turf.open_time and turf.close_time:
        current_time = datetime.combine(selected_date, turf.open_time)
        close_time = datetime.combine(selected_date, turf.close_time)
        
        while current_time < close_time:
            slot_start_time = current_time.time()
            end_of_slot = current_time + timedelta(minutes=30)
            
            slot_info = {
                'start_time': slot_start_time,
                'end_time': end_of_slot.time(),
                'status': 'available',
                'booking_obj': None,
            }

            if slot_start_time in booked_slots:
                booking = booked_slots[slot_start_time]
                slot_info['status'] = booking.status.lower()
                slot_info['booking_obj'] = booking

            slots.append(slot_info)
            current_time = end_of_slot

    context = {
        'turf': turf,
        'slots': slots,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
    }
    return render(request, 'owner-manage-slots.html', context)

# -----------------------------------------------------------------------------
# Placeholder Views for Static Pages
# -----------------------------------------------------------------------------
def cricket_view(request):
    return render(request, 'cricket.html')

def football_view(request):
    return render(request, 'football.html')

def badminton_view(request):
    return render(request, 'badminton.html')


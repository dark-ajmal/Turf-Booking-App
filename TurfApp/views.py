from django.shortcuts import render,redirect
from .models import Turf, Other_Turf
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.role == 'player':
                login(request, user)
                messages.success(request, "Login successful!")
                message = "Welcome, Player!"
                print(message)
                return redirect('home_view')
            else:
                login(request, user)
                messages.success(request, "Owner login successful!")
                return redirect('owner_view')
        
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        user_type = request.POST.get('user_type', 'player')  # Default to player
        
        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords don't match!")
            return render(request, "signup.html")
            
        if Turf.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "signup.html")

        try:
            user = Turf.objects.create_user(
                username=email,  # Using email as username
                name=name,
                password=password,
                email=email,
                phone=phone,
                role=user_type
            )
            user.save()
            
            # Automatically log in the user after signup
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Signup successful!")
                if user.role == 'player':
                    return redirect('home_view')
                else:
                    return redirect('owner_view')
                    
        except IntegrityError:
            messages.error(request, "Something went wrong. Please try again.")
            return render(request, "signup.html")
            
    return render(request, 'signup.html')



def landing_view(request):
    return render(request, 'landing.html')
def owner_view(request):
    return render(request, 'ownerdashboard.html')
def home_view(request):
    return render(request, 'home.html')
def ownerlogin_view(request):
    if request.method == 'POST':
        # Handle owner login logic here
        pass
    return render(request, 'owner_login.html')
def cricket_view(request):
    return render(request, 'cricket.html')
def football_view(request):

    return render(request, 'football.html')


def badminton_view(request):
    return render(request, 'badminton.html')


def turf_view(request):
    if request.method == 'POST':
       name= request.POST.get('name')
       sports_type = request.POST.get('sports_type')
       no_of_players = request.POST.get('no_of_players')
       price_per_hour = request.POST.get('price_per_hour')
       location = request.POST.get('location')
       image = request.FILES.get('image')
       owner = request.user

       Other_Turf.objects.create(
           name=name,
           sports_type=sports_type,
           no_of_players=no_of_players,
           price_per_hour=price_per_hour,
           location=location,
           image=image,
           owner=owner
       )
       messages.success(request, "Turf registered successfully!")
       return redirect('owner_view')

    return render(request, 'turfs.html')
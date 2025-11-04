from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile


# =========================
# LOGIN / LOGOUT
# =========================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('main:home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('users:login')


# =========================
# REGISTRATION FLOW
# =========================
def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')

    if request.method == 'POST':
        role = request.POST.get('user_type')
        if role == 'buyer':
            return redirect('users:registerdetails')
        elif role in ['seller', 'renter']:
            return redirect('users:sellerRenterdetails')

    return render(request, 'users/register.html')


def registerdetails_view(request):
    """Handles Buyer registration"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/registerdetails.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'users/registerdetails.html')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        UserProfile.objects.create(
            user=user,
            user_type='buyer',
            address=address,
            contact_number=contact_number
        )

        messages.success(request, "Buyer account created successfully!")
        return redirect('users:login')

    return render(request, 'users/registerdetails.html')


def sellerRenterdetails_view(request):
    """Handles Seller and Renter registration"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        driver_license = request.POST.get('driverliscence')
        role = request.POST.get('user_type')

        print("DEBUG ROLE VALUE:", role)

        if not role:
            messages.error(request, "User type not found in form.")
            return render(request, 'users/sellerRenterdetails.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/sellerRenterdetails.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'users/sellerRenterdetails.html')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        UserProfile.objects.create(
            user=user,
            user_type=role,
            address=address,
            contact_number=contact_number,
            driver_license=driver_license
        )

        messages.success(request, f"{role.capitalize()} account created successfully!")
        return redirect('users:login')

    return render(request, 'users/sellerRenterdetails.html')


# =========================
# VEHICLE UPLOAD
# =========================
@login_required
def uploadvehicles_view(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        price = request.POST.get('price')
        condition = request.POST.get('condition')
        vehicle_type = request.POST.get('type')
        description = request.POST.get('description')
        contact = request.POST.get('contact')
        images = request.FILES.get('images')

        Vehicle.objects.create(
            owner=profile,
            title=title,
            make=make,
            model=model,
            year=year,
            price=price,
            condition=condition,
            vehicle_type=vehicle_type,
            description=description,
            contact_number=contact,
            images=images
        )
        messages.success(request, "Vehicle uploaded successfully!")
        return redirect('main:home')

    return render(request, 'users/uploadvehicles.html')


# =========================
# PROFILE VIEW (Unified)
# =========================
@login_required
def profile_view(request):
    """Display unified profile for all roles"""
    profile = UserProfile.objects.get(user=request.user)
    user_type = profile.user_type

    vehicles = None
    saved_vehicles = None

    if user_type in ['seller', 'renter']:
        vehicles = Vehicle.objects.filter(owner=profile)
    elif user_type == 'buyer':
        saved_vehicles = SavedVehicle.objects.filter(user=profile)

    return render(request, 'profile/profile.html', {
        'profile': profile,
        'user_type': user_type,
        'vehicles': vehicles,
        'saved_vehicles': saved_vehicles,
    })

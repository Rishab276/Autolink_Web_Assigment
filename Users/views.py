# bhewa vigneshwar 2411725
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from Vehicles.models import Vehicle, VehicleImage
from Profile.models import SavedVehicle


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



def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')

    if request.method == 'POST':
        role = request.POST.get('user_type')
        print(f"DEBUG: Selected role in register_view: {role}")

        if role == 'buyer':
            return redirect('users:registerdetails')
        elif role in ['seller', 'renter']:
            return redirect('users:sellerRenterdetails_with_role', role=role)

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



def sellerRenterdetails_view(request, role=None):
    """Handles Seller and Renter registration"""
    print(f"DEBUG: Role parameter received: {role}")
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        driver_license = request.POST.get('driverliscence')
        
      
        submitted_role = request.POST.get('user_type')
        final_role = submitted_role if submitted_role else role

        print(f"DEBUG: Submitted role: {submitted_role}")
        print(f"DEBUG: Final role to save: {final_role}")

        if not final_role:
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
            user_type=final_role,  
            address=address,
            contact_number=contact_number,
            driver_license=driver_license
        )

        messages.success(request, f"{final_role.capitalize()} account created successfully!")
        return redirect('users:login')
    return render(request, 'users/sellerRenterdetails.html', {'selected_role': role})
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        driver_license = request.POST.get('driverliscence')
        submitted_role = request.POST.get('user_type')
        final_role = submitted_role if submitted_role else role
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


@login_required
def uploadvehicles_view(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
     
        make = request.POST.get('make')
        model_name = request.POST.get('model')
        year = request.POST.get('year')
        mileage = request.POST.get('mileage')
        transmission = request.POST.get('transmission')
        fuel_type = request.POST.get('fuel_type')
        vehicle_type = request.POST.get('type')
        price = request.POST.get('price')
        gps_coordinates = request.POST.get('gps_coordinates')
        description = request.POST.get('description')
        contact = request.POST.get('contact')  

        # Determine if it's for rent or sale
        is_rental = True if profile.user_type == "renter" else False

        vehicle = Vehicle.objects.create(
            uploader=request.user,
            make=make,
            model=model_name,
            year=year,
            mileage=mileage,
            transmission=transmission.capitalize() if transmission else 'Other',
            fuel_type=fuel_type.capitalize() if fuel_type else 'Other',
            type_of_vehicle=vehicle_type.capitalize() if vehicle_type else 'Car',
            price=price,
            contact=contact,
            gps_coor=gps_coordinates,
            is_rental=is_rental,
            desc=description,
        )

       
        images = request.FILES.getlist('images')
        for img in images:
            VehicleImage.objects.create(vehicle=vehicle, image=img)

        messages.success(request, "✅ Vehicle uploaded successfully!")
        return redirect('main:home')

    return render(request, 'users/uploadvehicles.html', {
        'user_type': profile.user_type,
    })


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

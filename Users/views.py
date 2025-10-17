from django.shortcuts import render
from django.contrib.auth import logout


def login_view(request):
    return render(request, 'Users/login.html')

def register_view(request):
    return render(request, 'Users/register.html')

def registerdetails_view(request):
    return render(request, 'Users/registerdetails.html')

def sellerRenterdetails_view(request):
    return render(request, 'Users/sellerRenterdetails.html')

def uploadvehicles_view(request):
    return render(request, 'Users/uploadvehicles.html')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import UserProfile, Vehicle



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('Main:home') 

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
            return redirect('home')  
        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'users/login.html')

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)  
    return redirect('users:login') 

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        role = request.POST.get('user_type')
        if role == 'buyer':
            return redirect('users:registerdetails')
        elif role in ['seller', 'renter']:
            return redirect('users:sellerRenterdetails')
    return render(request, 'users/register.html')



def registerdetails_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'users/registerdetails.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'users/registerdetails.html')

        user = User.objects.create_user(username=email,email=email, password=password,first_name=first_name, last_name=last_name)
        UserProfile.objects.create(user=user, address=address, contact_number=contact_number)
        messages.success(request, "Buyer account created successfully!")
        return redirect('users:login')
    return render(request, 'users/registerdetails.html')

def sellerRenterdetails_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        driver_license = request.POST.get('driverliscence')
        role = request.POST.get('user_type', 'seller') 
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'users/sellerRenterdetails.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'users/sellerRenterdetails.html')

        user = User.objects.create_user(username=email, email=email, password=password,first_name=first_name, last_name=last_name)
        UserProfile.objects.create(user=user, address=address,contact_number=contact_number, driver_license=driver_license)
        messages.success(request, "Seller/Renter account created successfully!")
        return redirect('users:login')
    return render(request, 'users/sellerRenterdetails.html')

from django.contrib.auth.decorators import login_required

@login_required
def uploadvehicles_view(request):
    if request.method == 'POST':
        seller_renter = UserProfile.objects.get(user=request.user)
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
            seller_renter=seller_renter,
            title=title,
            make=make,
            model=model,
            year=year,
            price=price,
            condition=condition,
            vehicle_type=vehicle_type,
            description=description,
            contact_number=contact,
            image=images
        )
        messages.success(request, "Vehicle uploaded successfully!")
        return redirect('home')  
    
    return render(request, 'users/uploadvehicles.html')


def uploadvehicles_view(request):
    return render(request, 'Users/uploadvehicles.html')
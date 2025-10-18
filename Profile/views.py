#bysalwan
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Vehicles.models import Vehicle
from Users.models import UserProfile
from .models import SavedVehicle

@login_required
def profile_view(request):
    """
    Display user profile with role-specific content:
    - Sellers → uploaded vehicles
    - Buyers → saved vehicles
    - Renters → rented vehicles (optional)
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    uploaded_vehicles = []
    saved_vehicles = []
    rented_vehicles = []

    if user_profile.user_type == 'seller':
        uploaded_vehicles = Vehicle.objects.filter(uploader=request.user).order_by('-id')

    elif user_profile.user_type == 'buyer':
        saved_vehicles = SavedVehicle.objects.filter(user=request.user).select_related('vehicle').order_by('-id')

    elif user_profile.user_type == 'renter':
        # Option 1: show rented vehicles if you have a Rental model
        # rented_vehicles = Rental.objects.filter(renter=request.user).select_related('vehicle').order_by('-id')
        # Option 2: leave empty for now
        rented_vehicles = []

    context = {
        'user_profile': user_profile,
        'uploaded_vehicles': uploaded_vehicles,
        'saved_vehicles': saved_vehicles,
        'rented_vehicles': rented_vehicles,
    }

    return render(request, 'profile.html', context)



@login_required
def remove_uploaded_vehicle(request, vehicle_id):
    """
    Allow sellers/renters to remove a vehicle they uploaded.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=user_profile)
    vehicle.delete()
    return redirect('profile:profile')


@login_required
def save_vehicle(request, vehicle_id):
    """
    Save a vehicle to the user's saved list (buyer only).
    """
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    SavedVehicle.objects.get_or_create(user=request.user, vehicle=vehicle)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_saved_vehicle(request, vehicle_id):
    """
    Remove a vehicle from the user's saved list (buyer only).
    """
    saved = get_object_or_404(SavedVehicle, user=request.user, vehicle__id=vehicle_id)
    saved.delete()
    return redirect('profile:profile')

@login_required
def toggle_save(request, vehicle_id):
    user = request.user
    vehicle = Vehicle.objects.get(id=vehicle_id)
    if vehicle in user.saved_vehicles.all():
        user.saved_vehicles.remove(vehicle)
        status = 'unsaved'
    else:
        user.saved_vehicles.add(vehicle)
        status = 'saved'
    return JsonResponse({'status': status})


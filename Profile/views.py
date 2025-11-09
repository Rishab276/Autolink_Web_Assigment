from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Vehicles.models import Vehicle, VehicleImage
from Users.models import UserProfile
from .models import SavedVehicle
from django.contrib import messages

@login_required
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    uploaded_vehicles = []
    saved_vehicles = []
    rented_vehicles = []

    print(f"DEBUG: User type: {user_profile.user_type}")

    if user_profile.user_type in ['seller', 'renter']:
        uploaded_vehicles = Vehicle.objects.filter(uploader=request.user).order_by('-id')
        print(f"DEBUG: Found {len(uploaded_vehicles)} uploaded vehicles")

    elif user_profile.user_type == 'buyer':
        saved_vehicles = SavedVehicle.objects.filter(user=request.user).select_related('vehicle').order_by('-saved_at')
        print(f"DEBUG: Found {len(saved_vehicles)} saved vehicles")
        
        for saved in saved_vehicles:
            print(f"DEBUG: Saved vehicle - {saved.vehicle.make} {saved.vehicle.model}")


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
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id, uploader=request.user)
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully!")
    except Vehicle.DoesNotExist:
        messages.error(request, "Vehicle not found or you don't have permission to delete it.")
    
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
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    try:
        saved_vehicle = SavedVehicle.objects.get(user=request.user, vehicle=vehicle)
        saved_vehicle.delete()
        print(f"DEBUG: Vehicle {vehicle_id} UNSAVED")
    except SavedVehicle.DoesNotExist:
        SavedVehicle.objects.create(user=request.user, vehicle=vehicle)  # Save
        print(f"DEBUG: Vehicle {vehicle_id} SAVED")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

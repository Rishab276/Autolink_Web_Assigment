# Profile/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Vehicles.models import Vehicle
from .models import SavedVehicle
from django.http import JsonResponse

@login_required
def saved_vehicles(request):
    saved = request.user.saved_vehicles.all()  # uses related_name
    return render(request, 'savedvehicles.html', {'saved_vehicles': saved})


@login_required
def save_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    SavedVehicle.objects.get_or_create(user=request.user, vehicle=vehicle)
    return redirect(request.META.get('HTTP_REFERER', '/'))  # redirect back


@login_required
def remove_saved_vehicle(request, vehicle_id):
    """Remove a vehicle from the logged-in user's saved vehicles."""
    saved = get_object_or_404(SavedVehicle, user=request.user, vehicle__id=vehicle_id)
    saved.delete()
    return redirect('savedvehicles')  # Redirect back to saved vehicles page

@login_required
def toggle_save_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    saved, created = SavedVehicle.objects.get_or_create(user=request.user, vehicle=vehicle)
    
    if not created:  # Already saved, so remove it
        saved.delete()
        status = 'removed'
    else:
        status = 'saved'
    
    return JsonResponse({'status': status})

@login_required
def profile_view(request):
    uploaded_vehicles = Vehicle.objects.filter(uploader=request.user)  # Assuming you add 'uploader' FK in Vehicle
    saved_vehicles = request.user.saved_vehicles.all()
    return render(request, 'profile.html', {
        'uploaded_vehicles': uploaded_vehicles,
        'saved_vehicles': saved_vehicles,
    })

@login_required
def remove_uploaded_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, uploader=request.user)
    vehicle.delete()
    return redirect('profile')

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
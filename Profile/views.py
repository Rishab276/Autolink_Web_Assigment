#MAIGHUN-2412258
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Vehicles.models import Vehicle
from Users.models import UserProfile
from .models import SavedVehicle
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import SimplePasswordChangeForm

# Display the user's profile page
@login_required
def profile_view(request):

    # Super Admin View
    if request.user.is_superuser:
        context = {
            "is_superadmin": True,
            "super_name": request.user.get_full_name() or request.user.username,
            "super_email": request.user.email,
        }
        return render(request, "superadmin_profile.html", context)

    # Buyer/Seller/Renter View
    user_profile = get_object_or_404(UserProfile, user=request.user)

    uploaded_vehicles = []
    saved_vehicles = []
    rented_vehicles = []

    print(f"DEBUG: User type: {user_profile.user_type}")

    if user_profile.user_type in ['seller', 'renter']:
        uploaded_vehicles = Vehicle.objects.filter(
            uploader=request.user
        ).order_by('-id')
        print(f"DEBUG: Found {len(uploaded_vehicles)} uploaded vehicles")

    elif user_profile.user_type == 'buyer':
        saved_vehicles = SavedVehicle.objects.filter(
            user=request.user,
            vehicle__is_sold=False
        ).select_related('vehicle').order_by('-saved_at')

        print(f"DEBUG: Found {len(saved_vehicles)} saved vehicles")

    context = {
        'user_profile': user_profile,
        'uploaded_vehicles': uploaded_vehicles,
        'saved_vehicles': saved_vehicles,
        'rented_vehicles': rented_vehicles,
        "is_superadmin": False,
    }
    return render(request, 'profile.html', context)

# Seller/Renter removes an uploaded vehicle
@login_required
def remove_uploaded_vehicle(request, vehicle_id):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id, uploader=request.user)
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully!")
    except Vehicle.DoesNotExist:
        messages.error(request, "Vehicle not found or you don't have permission to delete it.")
    
    return redirect('profile:profile')

# Buyer saves a vehicle
@login_required
def save_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    SavedVehicle.objects.get_or_create(user=request.user, vehicle=vehicle)
    return redirect(request.META.get('HTTP_REFERER', '/'))

# Buyer unsaves a vehicle
@login_required
def remove_saved_vehicle(request, vehicle_id):
    saved = get_object_or_404(SavedVehicle, user=request.user, vehicle__id=vehicle_id)
    saved.delete()
    return redirect('profile:profile')

# Toggle saving/unsaving a vehicle
@login_required
def toggle_save(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    try:
        # If vehicle is already saved, unsave it
        saved_vehicle = SavedVehicle.objects.get(user=request.user, vehicle=vehicle)
        saved_vehicle.delete()
        print(f"DEBUG: Vehicle {vehicle_id} UNSAVED")
    except SavedVehicle.DoesNotExist:
        # Otherwise, save it
        SavedVehicle.objects.create(user=request.user, vehicle=vehicle)
        print(f"DEBUG: Vehicle {vehicle_id} SAVED")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

# Seller marks a vehicle as sold
@login_required
def mark_as_sold(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, uploader=request.user)
    vehicle.is_sold = True
    vehicle.save()
    messages.success(request, "Vehicle marked as sold.")
    return redirect('profile:profile')

# Seller marks a vehicle as available again
@login_required
def unmark_as_sold(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, uploader=request.user)
    vehicle.is_sold = False
    vehicle.save()
    messages.success(request, "Vehicle is now available again.")
    return redirect('profile:profile')

# Renter marks a vehicle as rented
@login_required
def mark_as_rented(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, uploader=request.user)
    vehicle.is_rented = True
    vehicle.save()
    messages.success(request, "Vehicle marked as rented.")
    return redirect('profile:profile')

# Renter marks a vehicle as available again
@login_required
def unmark_as_rented(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, uploader=request.user)
    vehicle.is_rented = False
    vehicle.save()
    messages.success(request, "Vehicle is now available again.")
    return redirect('profile:profile')

# Password Change View
class CustomPasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'passwordchangeform.html'
    form_class = SimplePasswordChangeForm
    success_url = reverse_lazy('users:login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the user to the form
        return kwargs

    def form_valid(self, form):
        form.save()
        logout(self.request)
        messages.success(self.request, "Password changed successfully! Login again.")
        return super().form_valid(form)
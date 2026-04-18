from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from Vehicles.models import Vehicle
from Users.models import UserProfile
from .models import SavedVehicle
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import SimplePasswordChangeForm
import requests as http_requests

@login_required
def profile_view(request):
    if request.user.is_superuser:
        context = {
            "is_superadmin": True,
            "super_name":    request.user.get_full_name() or request.user.username,
            "super_email":   request.user.email,
        }
        return render(request, "superadmin_profile.html", context)

    user_profile      = get_object_or_404(UserProfile, user=request.user)
    uploaded_vehicles = []
    saved_vehicles    = []
    rented_vehicles   = []

    if user_profile.user_type in ['seller', 'renter']:
        uploaded_vehicles = Vehicle.objects.filter(
            uploader=request.user
        ).order_by('-id')
    elif user_profile.user_type == 'buyer':
        saved_vehicles = SavedVehicle.objects.filter(
            user=request.user,
            vehicle__is_sold=False
        ).select_related('vehicle').order_by('-saved_at')

    context = {
        'user_profile':      user_profile,
        'uploaded_vehicles': uploaded_vehicles,
        'saved_vehicles':    saved_vehicles,
        'rented_vehicles':   rented_vehicles,
        'is_superadmin':     False,
    }
    return render(request, 'profile.html', context)

@login_required
@require_POST
def ajax_unsave_vehicle(request, vehicle_id):
    """
    POST /profile/ajax-unsave/<vehicle_id>/
    jQuery AJAX endpoint — removes a saved vehicle.
    Returns JSON: { "success": true, "vehicle_id": 5 }
    Demonstrates: jQuery AJAX POST, JSON production & consumption
    """
    try:
        saved = SavedVehicle.objects.get(user=request.user, vehicle__id=vehicle_id)
        saved.delete()
        return JsonResponse({
            'success':    True,
            'vehicle_id': vehicle_id,
            'message':    'Vehicle removed from saved list.'
        })
    except SavedVehicle.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Vehicle not found.'}, status=404)

@login_required
@require_GET
def ajax_vehicle_weather(request, vehicle_id):
    """
    GET /profile/ajax-weather/<vehicle_id>/
    jQuery AJAX endpoint — fetches weather at vehicle's GPS location.
    Calls Open-Meteo API server-side, returns JSON to browser.
    Returns JSON: { "success": true, "temp": "27°C", "desc": "clear skies ☀️",
                    "city": "Curepipe", "sentence": "This car is listed in..." }
    Demonstrates: jQuery AJAX GET, JSON production, API consumption in Django
    """
    try:
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        gps = vehicle.gps_coor or ""

        if not gps:
            return JsonResponse({'success': False, 'message': 'No location set for this vehicle.'})

        parts = gps.split(',')
        lat   = float(parts[0].strip())
        lng   = float(parts[1].strip())

        # Reverse geocode city from Nominatim
        city = "this area"
        try:
            r = http_requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"lat": lat, "lon": lng, "format": "json"},
                headers={"User-Agent": "AutoLink-Django/1.0"},
                timeout=6,
            )
            addr = r.json().get("address", {})
            city = (
                addr.get("city") or addr.get("town") or addr.get("village")
                or addr.get("suburb") or addr.get("county") or "this area"
            )
        except Exception:
            pass

        # Fetch weather from Open-Meteo
        r = http_requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":      lat,
                "longitude":     lng,
                "current":       "temperature_2m,weather_code",
                "forecast_days": 1,
            },
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()

        temp = data["current"]["temperature_2m"]
        unit = data["current_units"]["temperature_2m"]
        code = int(data["current"]["weather_code"])

        desc   = _weather_desc(code)
        advice = _maybe_visit(code)
        vtype  = vehicle.type_of_vehicle.lower()

        sentence = (
            f"This {vtype} is listed in {city}, "
            f"currently {temp}{unit} and {desc} — {advice}"
        )

        return JsonResponse({
            'success':  True,
            'temp':     f"{temp}{unit}",
            'desc':     desc,
            'city':     city,
            'sentence': sentence,
            'code':     code,
        })

    except (ValueError, IndexError):
        return JsonResponse({'success': False, 'message': 'Invalid GPS coordinates.'})
    except Exception as ex:
        return JsonResponse({'success': False, 'message': str(ex)})


def _weather_desc(code):
    if code == 0:               return "clear skies ☀️"
    elif code in (1, 2):        return "partly cloudy 🌤️"
    elif code == 3:             return "overcast ☁️"
    elif code in range(45, 50): return "foggy 🌫️"
    elif code in range(51, 58): return "drizzling 🌦️"
    elif code in range(61, 68): return "raining 🌧️"
    elif code in range(71, 78): return "snowing ❄️"
    elif code in range(80, 83): return "rain showers 🌦️"
    elif code in range(95, 100):return "thunderstorming ⛈️"
    return "mixed conditions 🌡️"


def _maybe_visit(code):
    if code == 0:               return "great day to visit!"
    elif code in (1, 2):        return "not a bad day to visit."
    elif code == 3:             return "maybe bring a jacket."
    elif code in range(45, 50): return "drive carefully if you visit."
    elif code in range(51, 68): return "maybe visit tomorrow."
    elif code in range(71, 78): return "best to wait for better weather."
    elif code in range(80, 83): return "maybe visit tomorrow."
    elif code in range(95, 100):return "best to wait for better weather."
    return "check before visiting."

@login_required
@require_POST
def remove_uploaded_vehicle(request, vehicle_id):
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id, uploader=request.user)
        vehicle.delete()
        return JsonResponse({'success': True})
    except Vehicle.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@login_required
def save_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    SavedVehicle.objects.get_or_create(user=request.user, vehicle=vehicle)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def remove_saved_vehicle(request, vehicle_id):
    saved = get_object_or_404(SavedVehicle, user=request.user, vehicle__id=vehicle_id)
    saved.delete()
    return redirect('profile:profile')

@login_required
def toggle_save(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    try:
        saved_vehicle = SavedVehicle.objects.get(user=request.user, vehicle=vehicle)
        saved_vehicle.delete()
    except SavedVehicle.DoesNotExist:
        SavedVehicle.objects.create(user=request.user, vehicle=vehicle)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_POST
def toggle_sold(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, uploader=request.user)

    vehicle.is_sold = not vehicle.is_sold
    vehicle.save()

    if vehicle.is_sold:
        return JsonResponse({'status': 'sold'})
    else:
        return JsonResponse({'status': 'available'})

@login_required
@require_POST
def toggle_rented(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, uploader=request.user)

    vehicle.is_rented = not vehicle.is_rented
    vehicle.save()

    if vehicle.is_rented:
        return JsonResponse({'status': 'rented'})
    else:
        return JsonResponse({'status': 'available'})


class CustomPasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'passwordchangeform.html'
    form_class    = SimplePasswordChangeForm
    success_url   = reverse_lazy('users:login')

    def get_form_kwargs(self):
        kwargs         = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        logout(self.request)
        messages.success(self.request, "Password changed successfully! Login again.")
        return super().form_valid(form)
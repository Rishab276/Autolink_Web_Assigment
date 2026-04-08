# api/views.py
# These are the API endpoints that the Flet mobile app will call.
# Each view handles a specific URL and returns JSON data.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.db.models import Q
import math

from Vehicles.models import Vehicle
from Reviews.models import Review
from Profile.models import SavedVehicle
from Users.models import UserProfile

from .serializers import (
    VehicleSerializer,
    ReviewSerializer,
    ReviewSubmitSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    SavedVehicleSerializer,
)


# ============================================================
# AUTH ENDPOINTS
# ============================================================

class LoginAPI(APIView):
    """
    POST /api/login/
    Body: { "email": "...", "password": "..." }
    Returns: { "token": "...", "user_type": "...", "name": "..." }
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Find user by email
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check password
        user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get or create token (this is how we stay logged in on mobile)
        token, _ = Token.objects.get_or_create(user=user)

        # Get user type
        try:
            profile = UserProfile.objects.get(user=user)
            user_type = profile.user_type
        except UserProfile.DoesNotExist:
            user_type = 'buyer'

        return Response({
            'token': token.key,
            'user_type': user_type,
            'name': user.get_full_name() or user.username,
            'email': user.email,
        })


class RegisterAPI(APIView):
    """
    POST /api/register/
    Body: { "first_name", "last_name", "email", "password",
            "user_type", "address", "contact_number", "driver_license" }
    Returns: { "token": "...", "message": "..." }
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'message': 'Account created successfully!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPI(APIView):
    """
    POST /api/logout/
    Header: Authorization: Token <token>
    Deletes the token so user is logged out on mobile.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully.'})


class ProfileAPI(APIView):
    """
    GET /api/profile/
    Header: Authorization: Token <token>
    Returns the logged-in user's profile details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=404)


# ============================================================
# VEHICLE ENDPOINTS
# ============================================================

class VehicleListAPI(APIView):
    """
    GET /api/vehicles/
    Optional query params:
      ?search=toyota       - search by make/model
      ?type=Car            - filter by vehicle type
      ?min_price=100000    - filter by min price
      ?max_price=500000    - filter by max price
      ?is_rental=true      - show only rentals
    Returns: list of vehicles as JSON
    """
    def get(self, request):
        vehicles = Vehicle.objects.filter(
            is_sold=False, is_rented=False
        ).prefetch_related('images')

        # Search filter
        search = request.GET.get('search', '')
        if search:
            vehicles = vehicles.filter(
                Q(make__icontains=search) |
                Q(model__icontains=search) |
                Q(desc__icontains=search)
            )

        # Type filter (Car, Truck, Motorbike, etc.)
        vehicle_type = request.GET.get('type', '')
        if vehicle_type:
            vehicles = vehicles.filter(type_of_vehicle__iexact=vehicle_type)

        # Price filters
        min_price = request.GET.get('min_price', '')
        if min_price:
            vehicles = vehicles.filter(price__gte=min_price)

        max_price = request.GET.get('max_price', '')
        if max_price:
            vehicles = vehicles.filter(price__lte=max_price)

        # Rental filter
        is_rental = request.GET.get('is_rental', '')
        if is_rental.lower() == 'true':
            vehicles = vehicles.filter(is_rental=True)
        elif is_rental.lower() == 'false':
            vehicles = vehicles.filter(is_rental=False)

        serializer = VehicleSerializer(
            vehicles, many=True, context={'request': request}
        )
        return Response(serializer.data)


class VehicleDetailAPI(APIView):
    """
    GET /api/vehicles/<id>/
    Returns full details of a single vehicle including images.
    """
    def get(self, request, pk):
        try:
            vehicle = Vehicle.objects.prefetch_related('images').get(
                pk=pk, is_sold=False, is_rented=False
            )
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found.'}, status=404)

        serializer = VehicleSerializer(vehicle, context={'request': request})
        return Response(serializer.data)


class NearbyVehiclesAPI(APIView):
    """
    GET /api/vehicles/nearby/
    Query params: ?lat=<latitude>&lng=<longitude>&radius=20
    Uses the GPS coordinates stored in vehicles to find nearby ones.
    This is the SENSOR feature your lecturer asked for!
    
    How it works:
    - Flet app gets the user's GPS location from their phone
    - Sends lat/lng to this endpoint
    - Django calculates distance to each vehicle using Haversine formula
    - Returns only vehicles within the radius (default 20km)
    """
    def get(self, request):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = float(request.GET.get('radius', 20))  # km

        if not lat or not lng:
            return Response(
                {'error': 'lat and lng query parameters are required.'},
                status=400
            )

        try:
            user_lat = float(lat)
            user_lng = float(lng)
        except ValueError:
            return Response({'error': 'Invalid lat/lng values.'}, status=400)

        # Haversine formula - calculates distance between two GPS points
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat / 2) ** 2 +
                 math.cos(math.radians(lat1)) *
                 math.cos(math.radians(lat2)) *
                 math.sin(dlon / 2) ** 2)
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Get all vehicles that have GPS coordinates stored
        all_vehicles = Vehicle.objects.filter(
            is_sold=False,
            is_rented=False,
        ).exclude(gps_coor__isnull=True).exclude(gps_coor='').prefetch_related('images')

        nearby = []
        for vehicle in all_vehicles:
            try:
                # gps_coor is stored as "lat,lng" string e.g. "-20.1609,57.4977"
                parts = vehicle.gps_coor.split(',')
                v_lat = float(parts[0].strip())
                v_lng = float(parts[1].strip())
                distance = haversine(user_lat, user_lng, v_lat, v_lng)
                if distance <= radius:
                    nearby.append((distance, vehicle))
            except (ValueError, IndexError, AttributeError):
                continue  # Skip vehicles with bad GPS data

        # Sort by closest first
        nearby.sort(key=lambda x: x[0])
        vehicles = [v for _, v in nearby]

        serializer = VehicleSerializer(
            vehicles, many=True, context={'request': request}
        )
        return Response({
            'count': len(vehicles),
            'radius_km': radius,
            'vehicles': serializer.data
        })


# ============================================================
# REVIEW ENDPOINTS
# ============================================================

class ReviewListAPI(APIView):
    """
    GET /api/reviews/
    Returns all approved reviews.
    """
    def get(self, request):
        reviews = Review.objects.filter(is_approved=True).order_by('-created_date')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewSubmitAPI(APIView):
    """
    POST /api/reviews/submit/
    Body: { "title", "review_text", "rating", "author_name", "email" }
    Submits a new review (pending approval).
    """
    def post(self, request):
        serializer = ReviewSubmitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Review submitted! It will appear after approval.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# SAVED VEHICLES ENDPOINTS
# ============================================================

class SavedVehiclesAPI(APIView):
    """
    GET /api/saved/
    Header: Authorization: Token <token>
    Returns all vehicles saved by the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved = SavedVehicle.objects.filter(
            user=request.user,
            vehicle__is_sold=False
        ).select_related('vehicle').order_by('-saved_at')

        serializer = SavedVehicleSerializer(
            saved, many=True, context={'request': request}
        )
        return Response(serializer.data)


class ToggleSaveAPI(APIView):
    """
    POST /api/saved/toggle/<vehicle_id>/
    Header: Authorization: Token <token>
    Saves or unsaves a vehicle for the logged-in user.
    Returns: { "saved": true/false, "message": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, vehicle_id):
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found.'}, status=404)

        saved, created = SavedVehicle.objects.get_or_create(
            user=request.user, vehicle=vehicle
        )

        if not created:
            # Already saved — unsave it
            saved.delete()
            return Response({'saved': False, 'message': 'Vehicle removed from saved.'})

        return Response({'saved': True, 'message': 'Vehicle saved!'})

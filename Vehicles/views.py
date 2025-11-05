#bysalwan
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Vehicle
from django.core.paginator import Paginator
from Profile.models import SavedVehicle  # Import from Profile app

def standardsearch(request):
    vehicles = Vehicle.objects.all().order_by('id')
    paginator = Paginator(vehicles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    saved_vehicle_ids = []
    if request.user.is_authenticated:
        saved_vehicle_ids = list(SavedVehicle.objects.filter(
            user=request.user
        ).values_list('vehicle_id', flat=True))

    context = {
        'page_obj': page_obj,
        'all_vehicles': vehicles,  
        'saved_vehicle_ids': saved_vehicle_ids
    }
    return render(request, 'standardsearch.html', context)

def filter(request):
    return render(request, 'filter.html')

def detail(request, pk):
    vehicle_detail = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'detail.html', {'vehicle': vehicle_detail})

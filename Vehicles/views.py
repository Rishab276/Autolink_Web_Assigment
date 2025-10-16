from django.shortcuts import render, get_object_or_404
from .models import Vehicle
from django.core.paginator import Paginator

def standardsearch(request):
    vehicles = Vehicle.objects.all().order_by('id')
    paginator = Paginator(vehicles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'standardsearch.html',{'page_obj' : page_obj})

def filter(request):
    return render(request, 'filter.html')

def detail(request,pk):
    vehicle_detail = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'detail.html',{'vehicle': vehicle_detail})



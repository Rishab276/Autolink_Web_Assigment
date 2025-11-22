from django.shortcuts import render
from django.db.models import Count
from Vehicles.models import Vehicle
from Reviews.models import Review
from .forms import ContactForm

def Main(request):
    return render(request, 'Main.html')

def index(request):
    recent_vehicles = (
        Vehicle.objects
        .filter(is_sold = False, is_rented = False)
        .prefetch_related('images')
        .order_by('-id')[:4]
    )

    recent_reviews = (
        Review.objects
        .filter(is_approved=True)
        .order_by('-created_date')[:6]
    )

    category_counts = (
        Vehicle.objects
        .values('type_of_vehicle')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    total_vehicles = Vehicle.objects.count()
    contact_success = False

    if request.method == 'POST':
        contact_form = ContactForm(request.POST, request.FILES)
        if contact_form.is_valid():
            contact_form.save()
            contact_success = True
            contact_form = ContactForm() 
    else:
        contact_form = ContactForm()

    context = {
        'recent_vehicles': recent_vehicles,
        'recent_reviews': recent_reviews,
        'contact_form': contact_form,
        'contact_success': contact_success,
        'category_counts': category_counts,
        'total_vehicles': total_vehicles,
    }
    return render(request, 'index.html', context)

def faq(request):
    return render(request, 'faq.html')

def aboutus_view(request):
    return render(request, 'aboutus.html')

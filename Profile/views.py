from django.shortcuts import render

def saved_vehicles(request):
    # Toggle this to False if you want to test the "empty state"
    has_saved_vehicles = False

    # Dummy data (later replace with actual database data)
    saved_vehicles = []
    if has_saved_vehicles:
        saved_vehicles = [
            {
                'id': 1,
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2022,
                'price': 1000000,
                'mileage': 15000,
                'location': 'Port Louis',
                'vehicle_type': 'car',
                'image_path': 'savedvehicles/images/toyotacorolla.png'
            },
            {
                'id': 2,
                'make': 'Honda',
                'model': 'Civic',
                'year': 2021,
                'price': 975000,
                'mileage': 20000,
                'location': 'Curepipe',
                'vehicle_type': 'car',
                'image_path': 'savedvehicles/images/hondacivic.png'
            }
        ]

    context = {
        'has_saved_vehicles': has_saved_vehicles,
        'saved_vehicles': saved_vehicles
    }


    return render(request, 'savedvehicles.html', context)

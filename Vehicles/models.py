#bysalwan
from django.db import models
from django.contrib.auth.models import User

class Vehicle(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_vehicles', default=1)
    # Basic Info
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()

    # Specifications
    transmission = models.CharField(max_length=50, choices=[
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
        ('CVT', 'CVT'),
        ('Other', 'Other'),
    ],
        default='Manual'
    )
    fuel_type = models.CharField(max_length=50, choices=[
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Hybrid', 'Hybrid'),
        ('Electric', 'Electric'),
        ('Other', 'Other'),
    ],
        default='Petrol'
    )
    type_of_vehicle = models.CharField(max_length=50, choices=[
        ('Car', 'Car'),
        ('Truck', 'Truck'),
        ('Van', 'Van'),
        ('SUV', 'SUV'),
        ('Motorbike', 'Motorbike'),
        ('Bus', 'Bus'),
    ],
        default='Car'
    )

    # Other Details
    price = models.DecimalField(max_digits=10, decimal_places=0)
    gps_coor = models.CharField(max_length=100, blank=True, null=True)
    is_rental = models.BooleanField(default=False)
    desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"
    


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicle_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.vehicle.make} {self.vehicle.model}"
    
       

    


